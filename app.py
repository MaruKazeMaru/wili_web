import json
import os
from socket import timeout
import struct

from flask import Flask, \
    render_template, request, redirect, url_for, \
    send_from_directory
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import wilitools

from utils import *
from consts import MEDIA_ROOT_DIR, DB_PATH, STATIC_ROOT_DIR, TEMPLATE_ROOT_DIR
from forms import CreateAreaForm

app = Flask(
    __name__,
    static_folder=STATIC_ROOT_DIR,
    template_folder=TEMPLATE_ROOT_DIR
)

@app.route('/')
def index():
    return 'hello'


# this route is only for debug
@app.route('/media/<dir>/<filename>')
def media(dir:str, filename:str):
    return send_from_directory(os.path.join(MEDIA_ROOT_DIR, dir), filename)


# this route is for debug only
# @app.route('/media/<name>')
# def media(name:str):
#     ps = name.split('/')
#     if len(ps) > 1:
#         dir = os.path.sep.join(ps[0:-1])
#         dir = os.path.join(MEDIA_ROOT_DIR, dir)
#     else:
#         dir = MEDIA_ROOT_DIR
    
#     return send_from_directory(dir, ps[-1])


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
            form.blueprint.save(os.path.join(dir, 'blueprint.png'))
            with open(os.path.join(dir, 'blueprint_meta.json'), 'w') as f:
                json.dump(form.blueprint_meta, f)
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
    name, floor = db.get_area_meta(area_id)

    lap_img_name = 'motion_list_lap.png'
    dir = 'a{}'.format(area_id)
    img_dir = os.path.join(MEDIA_ROOT_DIR, dir)
    lap_img_path = os.path.join(img_dir, lap_img_name)

    with open(os.path.join(MEDIA_ROOT_DIR, dir, 'blueprint_meta.json'), mode='r') as fp:
        meta = json.load(fp)
        img_size = (meta['width'], meta['height'])

    create_motion_list_img(floor, gaussian.avrs, tr_prob, lap_img_path, img_size=img_size)

    blueprint = Image.open(os.path.join(img_dir, 'blueprint.png')).convert('RGB')
    bp = np.array(blueprint, dtype=np.float32)
    a = 0.25
    bp = bp * a + (255 * (1 - a))
    blueprint = Image.fromarray(bp.astype(np.uint8), mode='RGB').convert('RGBA')

    lap_img = Image.open(lap_img_path).convert('RGBA')

    img_name = 'motion_list.png'
    img = Image.alpha_composite(blueprint, lap_img)
    img.save(os.path.join(img_dir, img_name))

    img_route = '/media/{}/{}'.format(dir, img_name)

    return render_template(
        'motion_list.html',
        img_route=img_route
    )


@app.route('/suggest/<int:area_id>')
def suggest(area_id:int):
    db = wilitools.WiliDB(DB_PATH)

    name, floor = db.get_area_meta(area_id)

    init_prob = db.get_init_prob_all(area_id)
    tr_prob = db.get_tr_prob_mat(area_id)
    gaussian = db.get_gaussian_all(area_id)

    samples = db.get_samples(area_id)
    dens_samples = db.get_dens_samples(area_id)

    suggester = wilitools.Suggester(init_prob, tr_prob, gaussian, samples, dens_samples)
    weight = suggester.suggest()

    dir = 'a{}'.format(area_id)
    with open(os.path.join(MEDIA_ROOT_DIR, dir, 'blueprint_meta.json'), mode='r') as fp:
        meta = json.load(fp)
        img_size = (meta['width'], meta['height'])

    img_dir = os.path.join(MEDIA_ROOT_DIR, dir)

    lap_img_name = 'suggest_lap.png'
    lap_img_path = os.path.join(img_dir, lap_img_name)
    create_heatmap(gaussian, weight, floor, 0.3, lap_img_path, img_size=img_size)

    blueprint = Image.open(os.path.join(img_dir, 'blueprint.png')).convert('RGB')
    bp = np.array(blueprint, dtype=np.float32)
    a = 0.5
    bp = bp * a + (255 * (1 - a))
    blueprint = Image.fromarray(bp.astype(np.uint8), mode='RGB').convert('RGBA')
    # blueprint = Image.open(os.path.join(img_dir, 'blueprint.png')).convert('RGBA')
    # # bp = np.ndarray((img_size[1], img_size[0], 4), dtype=np.uint8)
    # # bp[:,:,[0,1,2]] = np.array(blueprint, dtype=np.uint8)
    # # bp[:,:,3] = 255
    # # blueprint = Image.fromarray(bp, mode='RGBA')

    lap_img = Image.open(lap_img_path).convert('RGB')
    li = np.ndarray((img_size[1], img_size[0], 4), np.uint8)
    li[:,:,[0,1,2]] = np.array(lap_img, dtype=np.uint8)
    li[:,:,3] = 191
    lap_img = Image.fromarray(li, mode='RGBA')

    img_name = 'suggest.png'
    img = Image.alpha_composite(blueprint, lap_img)
    img.save(os.path.join(img_dir, img_name))

    img_route = '/media/{}/{}'.format(dir, img_name)

    return render_template(
        'suggest.html',
        img_route=img_route
    )
