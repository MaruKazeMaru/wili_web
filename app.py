from flask import Flask, request, render_template, jsonify
from utils import socket_call_sync, heatmap_as_b64txt, gmm_to_arr_for_heatmap
import struct
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello'

@app.route('/suggest_test')
def suggest_test():
    # get values from ROS2 through socket
    suggest_res = socket_call_sync('socket', b'd', timeout=15)
    if suggest_res is None:
        return 500, 'socket timeout'

    heatmap_res = socket_call_sync('socket', b'c', timeout=15)
    if heatmap_res is None:
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
    vals = gmm_to_arr_for_heatmap( \
        n, weights, avrs, vars, \
        (-2, 2), (-2, 2), 20, 20 \
    )
    hm_b64 = heatmap_as_b64txt(vals)

    return render_template( \
        'show_suggest_result.html', \
        heatmap_png='data:image/png;base64,' + hm_b64 \
    )