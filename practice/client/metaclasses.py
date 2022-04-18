import dis
from socket import socket


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        if 'accept' in clsdict:
            raise TypeError('The class shouldn\'t have the method accept')
        if 'listen' in clsdict:
            raise TypeError('The class shouldn\'t have the method listen')
        for item in clsdict:
            if isinstance(clsdict[item],  socket):
                raise TypeError('The class shouldn\'t have the socket at the class level')

        type.__init__(self, clsname, bases, clsdict)
