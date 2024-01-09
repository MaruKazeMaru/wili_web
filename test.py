import os

import numpy as np
import matplotlib.pyplot as plt

import wilitools

from utils import create_motion_list_img

def main_():
    db = wilitools.WiliDB('db.sqlite3')
    suggester = wilitools.Suggester(
        db.get_init_prob_all(2),
        db.get_tr_prob_mat(2),
        db.get_gaussian_all(2),
        db.get_samples(2),
        db.get_dens_samples(2)
    )
    print(suggester.dens_sample)
    suggester.update(np.array([3,-1], dtype=np.float32))
    print(suggester.dens_sample)
    db.set_dens_samples(2, suggester.dens_sample)


def main():
    db = wilitools.WiliDB('db.sqlite3')
    samples = db.get_samples(2)
    dens_samples = db.get_dens_samples(2)

    # after miss prob
    ps = []
    p = samples[0]
    d_p = dens_samples[0]
    for i in range(1, 300):
        if d_p <= dens_samples[i] or dens_samples[i] >= d_p * np.random.rand():
            d_p = dens_samples[i]
            p = samples[i]

        if i % 3 == 2:
            ps.append(p.copy())
    ps = np.array(ps)

    plt.rcParams["font.size"] = 18
    fig1 = plt.figure(figsize=(4,4))
    ax = fig1.add_subplot()

    ax.set_xlabel('$\\theta_1$')
    ax.set_xticks([0,0.5,1])
    ax.set_xlim([-0.05, 1.05])

    ax.set_ylabel('$\\theta_2$')
    ax.set_yticks([0,0.5,1])
    ax.set_ylim([-0.05, 1.05])

    ax.scatter(ps[:,0], ps[:,1], s=120)
    fig1.tight_layout()
    fig1.subplots_adjust(left=0.22, right=0.98, bottom=0.22, top=0.98)
    fig1.savefig('miss_a.png')

    # before miss prob
    ps = []
    for i in range(100):
        ps.append(samples[i*3 + 2].copy())
    ps = np.array(ps)

    plt.rcParams["font.size"] = 18
    fig2 = plt.figure(figsize=(4,4))
    ax = fig2.add_subplot()

    ax.set_xlabel('$\\theta_1$')
    ax.set_xticks([0,0.5,1])
    ax.set_xlim([-0.05, 1.05])

    ax.set_ylabel('$\\theta_2$')
    ax.set_yticks([0,0.5,1])
    ax.set_ylim([-0.05, 1.05])

    ax.scatter(ps[:,0], ps[:,1], s=120)
    fig2.subplots_adjust(left=0.22, right=0.98, bottom=0.22, top=0.98)
    fig2.savefig('miss_b.png')


if __name__ == '__main__':
    main()
