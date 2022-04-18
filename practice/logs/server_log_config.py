import logging
import os
from logging import handlers
import sys
sys.path.append('../')
from common.variables import SERVER_LOG_NAME


PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')
fmt = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

server_handler = handlers.TimedRotatingFileHandler(PATH, 'midnight', 1, utc=False)
server_handler.setFormatter(fmt)
server_handler.setLevel(logging.DEBUG)

log = logging.getLogger(SERVER_LOG_NAME)
log.addHandler(server_handler)
