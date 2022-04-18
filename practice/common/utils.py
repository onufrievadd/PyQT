from .variables import DEFAULT_MAX_PACKAGE_LENGTH, DEFAULT_ENCODING
from .errors import IncorrectDataRecivedError, NonDictInputError
import json
from .decos import log


@log
def get_message(client):
    encoded_response = client.recv(DEFAULT_MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(DEFAULT_ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        else:
            raise IncorrectDataRecivedError
    else:
        raise IncorrectDataRecivedError


@log
def send_message(sock, message):
    if not isinstance(message, dict):
        raise NonDictInputError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(DEFAULT_ENCODING)
    sock.send(encoded_message)
