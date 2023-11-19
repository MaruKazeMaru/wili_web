import os
import numpy as np
from utils import create_motion_list_img

def uniform_simplex(dim:int):
    v = np.random.exponential(scale = 1, size=dim * dim).reshape((dim, dim))
    v = (v / np.sum(v, axis=0)).T
    return v


def main():
    x = np.random.uniform(-9, 9, 4)
    y = np.random.uniform(-5, 5, 4)
    avrs = np.vstack([x, y]).T
    print('avrs=')
    print(avrs)
    tr_prob = uniform_simplex(dim=4)
    print('tr_prob=')
    print(tr_prob)
    create_motion_list_img(
        avrs,
        tr_prob,
        '../motion_list.png',
        disp_range=(-8, -4.5, 8, 4.5)
    )

if __name__ == '__main__':
    main()
