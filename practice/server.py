import socket
import sys
import argparse
import logging
import select
import threading
sys.path.append('../')
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox
from logs import server_log_config
from common.variables import *
from common.utils import get_message, send_message
from common.decos import log
from descriptors import Port
from gui import *
from metaclassesserver import ServerVerifier
from database import ServerStorage

logger = logging.getLogger('server')
new_connection = False
conflag_lock = threading.Lock()


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default=DEFAULT_LISTEN_ADDR, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address, listen_port):
        self.sock = None
        self.addr = listen_address
        self.port = listen_port
        self.database = ServerStorage()

        self.clients = []

        self.messages = []

        self.names = {}

        super().__init__()

    def init_socket(self):
        logger.info(
            f'Запущен сервер, порт для подключений: {self.port} , адрес с которого принимаются '
            f'подключения: {self.addr}. Если адрес не указан, принимаются соединения с любых адресов.')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    def run(self):
        self.init_socket()

        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError):
                        logger.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError):
                    logger.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    def process_client_message(self, message, client):
        logger.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                ip_addr, port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], message[USER][PASSWORD], ip_addr, port)
                send_message(client, {RESPONSE: HTTP_200_OK, ALERT: 'OK'})
                with conflag_lock:
                    global new_connection
                    new_connection = True
            else:
                response = {RESPONSE: HTTP_400_BAD_REQUEST, ERROR: 'Имя пользователя уже занято.'}
                send_message(client, response)
                self.clients.remove(client)
                client.close()
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message \
                and self.names[message[USER]] == client:
            contacts = self.database.get_contacts(message[USER])
            response = {RESPONSE: HTTP_202_ACCEPTED, ALERT: contacts}
            send_message(client, response)
        elif ACTION in message and message[ACTION] == ADD_CONTACT and USER in message and CONTACT in message\
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[CONTACT])
            response = {RESPONSE: HTTP_200_OK, ALERT: 'OK'}
            send_message(client, response)
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and USER in message and CONTACT in message \
                and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[CONTACT])
            response = {RESPONSE: HTTP_200_OK, ALERT: 'OK'}
            send_message(client, response)
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            self.database.user_logout(message[ACCOUNT_NAME])
        else:
            response = HTTP_400_BAD_REQUEST
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)


def main():
    listen_address, listen_port = arg_parser()

    server = Server(listen_address, listen_port)
    server.daemon = True
    server.start()

    database = server.database

    app = QApplication(sys.argv)
    gui = MainWindow()

    gui.statusBar().showMessage('Server working...')
    gui.active_clients_table.setModel(gui_create_model(database))
    gui.active_clients_table.resizeColumnsToContents()
    gui.active_clients_table.resizeRowsToContents()

    def update_active_users():
        global new_connection
        if new_connection:
            gui.active_clients_table.setModel(gui_create_model(database))
            gui.active_clients_table.resizeColumnsToContents()
            gui.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistic():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(SERVER_DATABASE_PATH)
        config_window.db_file.insert(SERVER_DATABASE_NAME)
        config_window.port.insert(DEFAULT_PORT)
        config_window.ip.insert(DEFAULT_LISTEN_ADDR)
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        path = config_window.db_path.text()
        name = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            ip = config_window.ip.text()
            if 1024 <= port <= 65535:
                change_db_settings(path, name, port, ip)
                message.information(config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(config_window, 'Ошибка', 'Порт должен быть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(update_active_users)
    timer.start(1000)

    gui.refresh_button.triggered.connect(update_active_users)
    gui.show_history_button.triggered.connect(show_statistic)
    gui.config_btn.triggered.connect(server_config)

    app.exec_()


if __name__ == '__main__':
    main()
