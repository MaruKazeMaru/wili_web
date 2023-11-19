import sqlite3
import numpy as np
from numpy import ndarray


class db_operation:
    def __init__(self, db_path:str):
        self._con = sqlite3.connect(db_path)
        self._cur = self._con.cursor()


    def __del__(self):
        self._con.close()


    def get_motion_num(self) -> int:
        self._cur.execute('SELECT COUNT(id) FROM motion')
        return self._cur.fetchone()[0]


    def get_tr_prob_one(self, from_motion:int, to_motion: int) -> float:
        self._cur.execute(
            'SELECT data'
            + ' FROM tr_prob'
            + ' WHERE from_motion={} AND to_motion={}'.format(from_motion, to_motion)
        )
        return self._cur.fetchall()[0][0]


    def get_tr_prob_vec(self, from_motion:int) -> ndarray:
        n = self.get_motion_num()
        self._cur.execute(
            'SELECT data'
            + ' FROM tr_prob'
            + ' WHERE from_motion={}'.format(from_motion)
            + ' ORDER BY to_motion'
        )
        return np.array(self._cur.fetchall(), dtype='float32').reshape((n,))


    def get_tr_prob_mat(self) -> ndarray:
        n = self.get_motion_num()
        self._cur.execute(
            'SELECT data'
            + ' FROM tr_prob'
            + ' ORDER BY from_motion, to_motion'
        )
        return np.array(self._cur.fetchall(), dtype='float32').reshape((n, n))


    def get_gaussian_one(self, motion:int) -> tuple[ndarray, ndarray]:
        self._cur.execute(
            'SELECT avr_x, avr_y, covar_xx, covar_xy, covar_yy'
            + ' FROM gaussian'
            + ' WHERE motion={}'.format()
        )
        result = np.array(self._cur.fetchall()[0], dtype='float32')
        avr = result[[0, 1]]
        covar = np.ndarray((2, 2), dtype='float32')
        covar[0,0] = result[2]
        covar[0,1] = result[3]
        covar[1,0] = result[3]
        covar[1,1] = result[4]
        return avr, covar


    def get_gaussian_all(self) -> tuple[ndarray, ndarray]:
        self._cur.execute(
            'SELECT avr_x, avr_y, covar_xx, covar_xy, covar_yy'
            + ' FROM gaussian'
            + ' ORDER BY motion'
        )
        result = np.array(self._cur.fetchall(), dtype='float32')
        avrs = result[:, [0, 1]]
        covars = ndarray((2, 2), dtype='float32')
        covars[:,0,0] = result[:,2]
        covars[:,0,1] = result[:,3]
        covars[:,1,0] = result[:,3]
        covars[:,1,1] = result[:,4]
        return avrs, covars
