import numpy as np
from numpy import ndarray
import PIL
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

from wilitools import Suggester, Area, area_to_suggester, Gaussian, Floor

def create_motion_list_img(
    floor:Floor,
    avrs:ndarray, tr_prob:ndarray,
    path:str, img_size:tuple[float,float]=(960,540)
):
    n = tr_prob.shape[0]

    centers = avrs - np.array((floor.xmin, floor.ymax))
    centers = np.array([
        img_size[0] / (floor.xmax - floor.xmin),
        -img_size[1] / (floor.ymax - floor.ymin)
    ]) * centers
    centers = centers.astype('float32')

    coef = (img_size[0] + img_size[1]) / (960 + 560)
    icon_radius = int(coef * 50)
    line_dist   = int(coef * 12)
    line_width  = int(coef *  6)
    font_size   = int(coef * 50)
    ah_size     = int(coef * 20) # arrow head size

    img = Image.new('LA', img_size, (0,0))
    draw = ImageDraw.Draw(img)

    temp = tr_prob.flatten().argsort()
    froms = np.floor(temp / n).astype('uint8')
    tos = (temp - n * froms).astype('uint8')
    del temp
    tr_prob_max = tr_prob[froms[-1], tos[-1]]

    # 90[deg] ccw rotation
    r90 = np.array([[0, 1], [-1, 0]], dtype='float32')
    # rotation for arrow head
    ang = 2 * np.pi / 10
    cos = np.cos(ang)
    sin = np.sin(ang)
    r_ah = np.array([[cos, sin], [-sin, cos]], dtype='float32')

    # draw edge=transition probability
    for f, t in zip(froms, tos):
        # c = 255 - int(np.floor(255 * tr_prob[f,t] / tr_prob_max))
        a = int(np.floor(255 * tr_prob[f,t] / tr_prob_max))

        if f == t:
            box = [
                centers[f,0] + 0.5 * icon_radius, centers[f,1] - 0.7 * icon_radius,
                centers[f,0] + 2   * icon_radius, centers[f,1] + 0.7 * icon_radius
            ]
            box = [int(v) for v in box]
            draw.arc(
                box,
                0, 360,
                fill=(0, a),width=line_width
            )
            ah_s = np.array([centers[f,0] + 1.92 * icon_radius, centers[f,1]]) # arrow head start
            ah_tan = np.array([-0.2, 0.98]) # arrow head tangent
        else:
            d = (centers[t] - centers[f])
            d = d / np.linalg.norm(d)
            ah_tan = d # arrow head tangent
            d = line_dist * r90 @ d
            s = centers[f] + d # arrow start
            e = centers[t] + d # arrow end
            box = [s[0], s[1], e[0], e[1]]
            box = [int(v) for v in box]
            ah_s = (s + e) / 2 # arrow head start
            draw.line(
                box,
                fill=(0,a), width=line_width
            )

        # draw arrow head
        ah_e = ah_s + ah_size * r_ah @ ah_tan
        bbox = [ah_s[0], ah_s[1], ah_e[0], ah_e[1]]
        bbox = [int(v) for v in bbox]
        draw.line(
            bbox,
            fill=(0,a), width=line_width
        )
        ah_e = ah_s + ah_size * r_ah.T @ ah_tan
        bbox = [ah_s[0], ah_s[1], ah_e[0], ah_e[1]]
        bbox = [int(v) for v in bbox]
        draw.line(
            bbox,
            fill=(0,a), width=line_width
        )

    # draw node=motion
    font = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf', size=font_size)
    for i in range(n):
        bbox = [
            centers[i,0] - icon_radius, centers[i,1] - icon_radius,
            centers[i,0] + icon_radius, centers[i,1] + icon_radius
        ]
        bbox = [int(v) for v in bbox]
        draw.ellipse(
            bbox,
            fill=(255,255), outline=(0,255), width=line_width
        )

        c = [centers[i,0], centers[i,1]]
        c = [int(v) for v in c]
        draw.text(
            c, '{}'.format(i + 1),
            font=font, anchor='mm', fill=(0, 255)
        )

    img.save(path)

    return


def create_heatmap(path:str, gaussian:Gaussian, weight:ndarray, floor:Floor, delta:float):
    x = floor.lattice_from_delta(delta)
    nr = x.shape[1]
    nc = x.shape[0]
    h = gaussian.weighted(x.reshape((nr * nc, 2)), weight)
    h = h.reshape(nc, nr, 2)
    fig = plt.figure(dpi=1, figsize=(nc, nr))
    ax = fig.add_axes()
    ax.axis('off')
    ax.pcolor(h)
    fig.savefig(path)
