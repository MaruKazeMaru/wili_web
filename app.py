import os
from socket import timeout
import struct

from flask import Flask, \
    render_template, request, redirect, url_for
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import wilitools

from utils import *
from consts import MEDIA_ROOT_DIR, DB_PATH
from forms import CreateAreaForm

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello'

@app.route('/suggest_test')
def suggest_test():
    # get values from ROS2 through socket
    try:
        suggest_res = socket_call_sync('socket', b'd', timeout=15)
    except timeout:
        return 500, 'socket timeout'

    try:
        heatmap_res = socket_call_sync('socket', b'c', timeout=15)
    except timeout:
        return 500, 'socket timeout'

    if not heatmap_res[0] == suggest_res[0]:
        return 500, 'contradiction'

    n = suggest_res[0]

    # gaussian
    fmt = 'f' * (5 * n)
    fmt = '<' + fmt
    hs = np.array( \
        struct.unpack(fmt, heatmap_res[1:]), \
        dtype=np.float32, \
    )
    hs = hs.reshape((n,5))
    avrs = hs[:,[0,1]]
    vars = np.ndarray((n, 2, 2), dtype=np.float32)
    vars[:,0,0] = hs[:,2]
    vars[:,0,1] = hs[:,3]
    vars[:,1,0] = hs[:,3]
    vars[:,1,1] = hs[:,4]

    # weight
    fmt = 'f' * n
    weights = np.array( \
        struct.unpack('<' + fmt, suggest_res[1:]), \
        dtype=np.float32 \
    )

    # create heatmap
    x_step = 50
    y_step = 50
    vals = gmm_to_arr_for_heatmap( \
        n, weights, avrs, vars, \
        (-3, 3), (-3, 3), x_step, y_step \
    )

    fig, ax = plt.subplots(figsize=(x_step, y_step))
    ax.pcolor(vals)
    plt.axis('tight')
    plt.axis('off')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.savefig(MEDIA_ROOT_DIR + 'suggest_result.png')

    return render_template('show_suggest_result.html')

@app.route('/tr_prob')
def tr_prob():
    try:
        tr_prob = get_tr_prob('socket', timeout=10)
    except timeout:
        return 500, 'socket timeout'
    
    return render_template(
        'tr_prob.html',
        tr_prob=tr_prob
    )


@app.route('/create_area', methods=['GET', 'POST'])
def create_area():
    if request.method == 'POST':
        db = wilitools.WiliDB(DB_PATH)
        form = CreateAreaForm(db)
        request_is_valid = form.validate(request)
        if request_is_valid:
            im_w, im_h = form.blueprint.size
            x = form.width / 2
            y = x * im_h / im_w
            area_id = db.insert_area(
                wilitools.create_area(form.name, wilitools.Floor(-x, x, -y, y))
            )
            dir = os.path.join(MEDIA_ROOT_DIR, 'a{}'.format(area_id))
            os.makedirs(dir, mode=0o775, exist_ok=True)
            form.blueprint.save(os.path.join(dir, 'blueprint' + form.blueprint_ext))
            return redirect(url_for('success_create_area', area_id=area_id))
        else:
            print(form.errs)
            return render_template('create_area.html', errs=form.errs)
    else:
        return render_template('create_area.html', errs={})


@app.route('/success_create_area/<int:area_id>', methods=['GET'])
def success_create_area(area_id:int):
    return render_template('success_create_area.html', area_id=area_id)


@app.route('/motion_list/<int:area_id>')
def motion_list(area_id:int):
    db = wilitools.WiliDB(DB_PATH)
    tr_prob = db.get_tr_prob_mat(area_id)
    gaussian = db.get_gaussian_all(area_id)

    img_name = 'motion_list.png'
    img_path = os.path.join(MEDIA_ROOT_DIR, img_name)
    img_route = '/media/' + img_name
    create_motion_list_img(gaussian.avrs, tr_prob, img_path)
    return render_template(
        'motion_list.html',
        motion_list_img=img_route
    )
