from utils import *
import numpy as np
import base64

def gmm():
    n = 3
    w = np.array([1, 1, 1], dtype=np.float32)
    avr = np.array([[2,0], [-1,1.73], [-1,-1.73]], dtype=np.float32)
    var = np.array([[[1,0],[0,1]], [[1,0],[0,1]], [[1,0],[0,1]]], dtype=np.float32)
    vals = gmm_to_arr_for_heatmap( \
        n, w, avr, var, \
        (-2,2), (-2,2), 7, 7 \
    )
    return vals


def heatmap():
    img_bytes = base64.b64decode(heatmap_as_b64txt(gmm()))
    with open('test.png', mode='wb') as f:
        f.write(img_bytes)


if __name__ == '__main__':
    heatmap()