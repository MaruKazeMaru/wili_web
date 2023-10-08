from flask import Flask, request, render_template, jsonify
from utils import socket_call_sync, heatmap_as_b64txt
import struct
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello'

@app.route('/suggest_test')
def suggest_test():
    suggest_res = socket_call_sync('socket', b'd', timeout=15)
    if suggest_res is None:
        return 500, 'socket timeout'

    heatmap_res = socket_call_sync('socket', b'c', timeout=15)
    if heatmap_res is None:
        return 500, 'socket timeout'

    if not heatmap_res[0] == suggest_res[0]:
        return 500, 'contradiction'

    n = suggest_res[0]

    fmt = 'f' * (5 * n)
    hs = np.array(struct.unpack('<' + fmt, heatmap_res[1:]))
    hs = hs.reshape((n,5))
    avrs = hs[:,[0,1]]
    vars = hs[:,[2,3,4]]
    
    fmt = 'f' * n
    weights = struct.unpack('<' + fmt, suggest_res[1:])

    heatmap_params = {
        'motion_num': n,
        'weights': weights,
        'avrs': avrs.tolist(),
        'vars': vars.tolist(),
    }
    #return jsonify(heatmap_params)
    return render_template('show_suggest_result.html', heatmap_params=heatmap_params)