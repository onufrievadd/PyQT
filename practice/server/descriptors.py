import sys
sys.path.append('../')
from common.settings import DEFAULT_PORT


class Port:
    def __set_name__(self, owner, name):
        self.port = name

    def __set__(self, instance, value):
        if not 1124 <= value <= 65535:
            instance.__dict__[self.port] = DEFAULT_PORT
        else:
            instance.__dict__[self.port] = value
