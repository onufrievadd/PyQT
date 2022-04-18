import logging
import os
from logging import handlers
import sys
sys.path.append('../')
from common.variables import CLIENT_LOG_NAME


PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')
fmt = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

client_handler = handlers.TimedRotatingFileHandler(PATH, 'midnight', 1, utc=False)
client_handler.setFormatter(fmt)
client_handler.setLevel(logging.DEBUG)

log = logging.getLogger(CLIENT_LOG_NAME)
log.addHandler(client_handler)
