import struct

class Messages:
    """
    All messages that can be sent down the socket.
    """
    AddProxy, DelProxy, GetProxies, Success, Failure = range(2, 7)

def read_host_port(socket):
    """
    Reads a single host-port pair off the socket.
    """
    unpacking_recv = lambda sz, fmt: struct.unpack(fmt, socket.recv(sz))[0]
    host_sz = unpacking_recv(4, "@I")
    host = socket.recv(host_sz)
    port = unpacking_recv(4, "@I")
    return (host, port)

def read_message(socket):
    """
    Reads a message packet off the socket, returning the tuple
    (MessageType, Params) or a boolean if it is a success/fail message.
    """
    msg_type = struct.unpack("@B", socket.recv(1))[0]

    if msg_type == Messages.AddProxy:
        src = read_host_port(socket)
        dest = read_host_port(socket)
        return (Messages.AddProxy, (src, dest))
    elif msg_type == Messages.DelProxy:
        src = read_host_port(socket)
        return (Messages.DelProxy, src)
    elif msg_type == Messages.GetProxies:
        num_proxies = struct.unpack("@I", socket.recv(4))[0]
        proxies = []
        for x in xrange(num_proxies):
            src = read_host_port(socket)
            dest = read_host_port(socket)
            proxies.append((src, dest))
        return (Messages.GetProxies, proxies)
    elif msg_type in (1, 0):
        return bool(msg_type)
    else:
        raise ValueError("{} is not a valid message!".format(msg_type))

def write_host_port(socket, host, port):
    """
    Writes a single host-port pair to the socket.
    """ 
    packing_send = lambda val, fmt: socket.send(struct.pack(fmt, val))
    packing_send(len(host), "@I")
    socket.send(host)
    packing_send(port, "@I")

def write_message(socket, msg):
    """
    Writes a single message to the socket.
    """

    if type(msg) == bool and msg in (True, False):
        socket.send(struct.pack("@B", msg))
        return

    msgtype, params = msg
    socket.send(struct.pack("@B", msgtype))
    if msgtype == Messages.AddProxy:
        write_host_port(socket, params[0][0], params[0][1])
        write_host_port(socket, params[1][0], params[1][1])
    elif msgtype == Messages.DelProxy:
        write_host_port(socket, params[0], params[1])
    elif msgtype == Messages.GetProxies:
        socket.send(struct.pack("@I", len(params)))
        for param in params:
            write_host_port(socket, param[0][0], param[0][1])
            write_host_port(socket, param[1][0], param[1][1])
    else:
        raise ValueError("{} is not a valid message!".format(msg_type))