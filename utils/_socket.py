import socket
import struct
import numpy as np
from numpy import ndarray

def socket_call_sync(file_name:str, request:bytes, timeout=60) -> bytes:
    sock = socket.socket( \
        family=socket.AF_UNIX, \
        type=socket.SOCK_STREAM, \
        proto=0 \
    )
    sock.settimeout(timeout)
    sock.connect('/tmp/wili/{}.socket'.format(file_name))
    sock.send(request)
    response = sock.recv(1024)
    sock.close()
    return response


def get_motion_num(socket_file_name:str, timeout=60) -> int:
    res = socket_call_sync(socket_file_name, b'a', timeout=15)
    return res[0]


def get_tr_prob(socket_file_name:str, timeout=60) -> ndarray:
    res = socket_call_sync(socket_file_name, b'b', timeout=15)

    n = res[0]
    fmt = 'f' * (n * n)
    fmt = '<' + fmt
    tr_prob = struct.unpack(fmt, res[1:])
    tr_prob = np.array(tr_prob).reshape((n,n))

    return tr_prob


def get_heatmaps(socket_file_name:str, timeout=60) -> (ndarray, ndarray):
    res = socket_call_sync(socket_file_name, b'c', timeout=15)

    n = res[0]
    fmt = 'f' * (5 * n)
    fmt = '<' + fmt
    heatmaps = struct.unpack(fmt, res[1:])
    heatmaps = np.array(heatmaps).reshape((n,5))

    return heatmaps


def get_suggest(socket_file_name:str, timeout=60) -> ndarray:
    res = socket_call_sync(socket_file_name, b'b', timeout=15)

    n = res[0]
    fmt = 'f' * n
    fmt = '<' + fmt
    weight = struct.unpack(fmt, res[1:])
    weight = np.array(weight)

    return weight