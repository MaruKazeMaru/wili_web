import numpy as np
from numpy import ndarray

def gmm_to_arr_for_heatmap( \
    n:int,
    weights:ndarray,
    avrs:ndarray, vars:ndarray, \
    x_range:tuple[float,float], \
    y_range:tuple[float,float], \
    x_step:int, y_step:int
) -> ndarray:
    m = x_step * y_step
    x, y = np.meshgrid( \
        np.linspace(x_range[0], x_range[1], x_step, dtype=np.float32), \
        np.linspace(y_range[0], y_range[1], y_step, dtype=np.float32) \
    )
    x = x.flatten()
    y = y.flatten()
    x_ = np.stack([x,y]).T.reshape((1, m, 2)) - avrs.reshape((n, 1, 2))
    # print(x_)

    temp = x_ @ np.linalg.inv(vars)
    temp = temp * x_
    temp = np.sum(temp, dtype=np.float32, axis=2)
    temp = np.exp(-0.5 * temp, dtype=np.float32)

    coef = np.linalg.det(vars)
    coef = np.abs(coef)
    coef = np.sqrt(coef, dtype=np.float32)
    coef = weights / coef
    coef /= 2.0 * np.pi
    # print(coef)

    temp = coef.reshape((n,1)) * temp
    # print(temp)
    temp = np.sum(temp, axis=0)

    return temp.reshape((x_step, y_step))