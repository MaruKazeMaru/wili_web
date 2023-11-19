import numpy as np
from numpy import ndarray
import PIL
from PIL import Image, ImageDraw, ImageFont

def create_motion_list_img(
    avrs:ndarray, tr_prob:ndarray, path:str,
    disp_range:tuple[float, float, float, float]=(-5,-5,5,5),
    img_size:tuple[float,float]=(960,540)
):
    n = tr_prob.shape[0]

    centers = avrs - np.array((disp_range[0], disp_range[3]))
    centers = np.array([
        img_size[0] / (disp_range[2] - disp_range[0]),
        -img_size[1] / (disp_range[3] - disp_range[1])
    ]) * centers
    centers = centers.astype('float32')

    coef = (img_size[0] + img_size[1]) / (960 + 560)
    icon_radius = coef * 50
    line_dist   = coef * 12
    line_width  = coef *  6
    font_size   = coef * 50
    ah_size     = coef * 20 # arrow head size

    img = Image.new('L', img_size, (255,))
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
        c = 255 - int(np.floor(255 * tr_prob[f,t] / tr_prob_max))

        if f == t:
            box = (
                (centers[f,0] + 0.5 * icon_radius, centers[f,1] - 0.7 * icon_radius),
                (centers[f,0] + 2   * icon_radius, centers[f,1] + 0.7 * icon_radius)
            )
            draw.arc(
                box,
                0, 360,
                fill=c,width=line_width
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
            ah_s = (s + e) / 2 # arrow head start
            draw.line(
                (s[0], s[1], e[0], e[1]),
                fill=(c,), width=line_width
            )

        # draw arrow head
        ah_e = ah_s + ah_size * r_ah @ ah_tan
        draw.line(
            (ah_s[0], ah_s[1], ah_e[0], ah_e[1]),
            fill=(c,), width=line_width
        )
        ah_e = ah_s + ah_size * r_ah.T @ ah_tan
        draw.line(
            (ah_s[0], ah_s[1], ah_e[0], ah_e[1]),
            fill=(c,), width=line_width
        )

    # draw node=motion
    font = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf', size=font_size)
    for i in range(n):
        draw.ellipse(
            (centers[i,0] - icon_radius, centers[i,1] - icon_radius, centers[i,0] + icon_radius, centers[i,1] + icon_radius),
            fill=(255,), outline=(0,), width=line_width
        )

        draw.text(
            (centers[i,0], centers[i,1]), '{}'.format(i + 1),
            font=font, anchor='mm'
        )

    img.save(path)

    return
