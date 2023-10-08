import socket

def socket_call_sync(file_name:str, request:bytes, timeout=60) -> bytes:
    sock = socket.socket( \
        family=socket.AF_UNIX, \
        type=socket.SOCK_STREAM, \
        proto=0 \
    )
    sock.settimeout(timeout)
    try:
        sock.connect('/tmp/wili/{}.socket'.format(file_name))
        sock.send(request)
        response = sock.recv(1024)
        sock.close()
        return response
    except socket.timeout:
        return None
