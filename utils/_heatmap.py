import numpy as np
from numpy import ndarray
from PIL import Image
import io
import base64

def heatmap_as_b64txt(values:ndarray):
    vs = values / np.max(values)
    vs *= 255
    vs = vs.astype(np.uint8)
    img_np = ndarray((vs.shape[0], vs.shape[1], 3), dtype=np.uint8)
    img_np[:,:,0] = vs
    img_np[:,:,1] = vs
    img_np[:,:,2] = vs

    bytes_io = io.BytesIO()

    img_pil = Image.fromarray(img_np)
    img_pil.save(bytes_io, format='PNG')
    img_bytes = bytes_io.getvalue()
    return base64.b64encode(img_bytes).decode()