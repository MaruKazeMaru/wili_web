from flask import Flask, render_template
import struct
import numpy as np
import matplotlib.pyplot as plt
from socket import timeout

from utils import *
from consts import MEDIA_ROOT

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
    plt.savefig(MEDIA_ROOT + 'suggest_result.png')

    return render_template('show_suggest_result.html')

@app.route('/tr_prob')
def tr_prob():
    try:
        tr_prob = get_tr_prob('socket', timeout=10)
    except timeout:
        return 500, 'socket timeout'
    
    return render_template( \
        'tr_prob.html', \
        tr_prob=tr_prob \
    )