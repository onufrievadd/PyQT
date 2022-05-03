
DEFAULT_PORT = 7777

DEFAULT_IP_ADDR = '127.0.0.1'

DEFAULT_LISTEN_ADDR = ''

DEFAULT_QUEUE_LENGTH = 100

DEFAULT_MAX_PACKAGE_LENGTH = 1024

DEFAULT_ENCODING = 'utf-8'

SERVER_DATABASE_PATH = 'sqlite:///'
SERVER_DATABASE_NAME = 'server.sqlite'

ACTION = 'action'
TIME = 'time'
USER = 'user'
CONTACT = 'contact'
SENDER = 'sender'
DESTINATION = 'destination'

ACCOUNT_NAME = 'account_name'
PASSWORD = 'password'

PRESENCE = 'presence'
GET_CONTACTS = 'get contacts'
ADD_CONTACT = 'add contact'
MESSAGE = 'message'
REMOVE_CONTACT = 'remove contact'
EXIT = 'exit'

RESPONSE = 'response'
MESSAGE_TEXT = 'message_text'
ERROR = 'error'
ALERT = 'alert'

HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_202_ACCEPTED = 202

CLIENT_LOG_NAME = 'client'
SERVER_LOG_NAME = 'server'


def change_db_settings(path, name, port, ip):
    global SERVER_DATABASE_PATH, SERVER_DATABASE_NAME, DEFAULT_PORT, DEFAULT_LISTEN_ADDR
    SERVER_DATABASE_PATH = path
    SERVER_DATABASE_NAME = name
    DEFAULT_PORT = port
    DEFAULT_LISTEN_ADDR = ip