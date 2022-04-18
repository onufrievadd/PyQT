import dis
from socket import socket


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        if 'connect' in clsdict:
            raise TypeError('The class shouldn\'t have the method connect')

        SOCK_STREAM = False
        AF_INET = False
        for func in clsdict:
            try:
                if isinstance(clsdict[func], socket):
                    raise TypeError('The class shouldn\'t have the socket at the class level')
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for item in ret:
                    if item.argval == 'AF_INET':
                        AF_INET = True
                    elif item.argval == 'SOCK_STREAM':
                        SOCK_STREAM = True

        if not (SOCK_STREAM and AF_INET):
            raise TypeError('Socket protocol must be TCP')

        type.__init__(self, clsname, bases, clsdict)
