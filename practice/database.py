from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker, scoped_session
from datetime import datetime
import sys
sys.path.append('../')
from common.variables import SERVER_DATABASE_NAME, SERVER_DATABASE_PATH


class ServerStorage:
    class Users:
        def __init__(self, username, password):
            self.id = None
            self.username = username
            self.password = password
            self.last_login = datetime.now()

    class ActiveUsers:
        def __init__(self, user_id, ip_address, port):
            self.id = None
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = datetime.now()

    class UsersLoginsHistory:
        def __init__(self, user_id, ip_address, port):
            self.id = None
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = datetime.now()

    class Contacts:
        def __init__(self, user_id, contact):
            self.id = None
            self.user = user_id
            self.contact = contact
            self.connection_created_at = datetime.now()

    class UsersHistories:
        def __init__(self, user_id):
            self.id = None
            self.user = user_id
            self.send = 0
            self.accept = 0

    def __init__(self):
        self.database = create_engine(SERVER_DATABASE_PATH + SERVER_DATABASE_NAME, echo=False, pool_recycle=7200, connect_args={
            'check_same_thread': False})
        self.metadata = MetaData()

        users = Table('Users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String, unique=True),
                      Column('password', String),
                      Column('last_login', DateTime)
                      )

        active_users = Table('Active_users', self.metadata,
                             Column('id', Integer, primary_key=True),
                             Column('user', ForeignKey('Users.id'), unique=True),
                             Column('ip_address', String),
                             Column('port', Integer),
                             Column('login_time', DateTime)
                             )

        users_logins_history = Table('Users_logins_history', self.metadata,
                                     Column('id', Integer, primary_key=True),
                                     Column('user', ForeignKey('Users.id')),
                                     Column('ip_address', String),
                                     Column('port', Integer),
                                     Column('login_time', DateTime),
                                     )

        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', String),
                         Column('connection_created_at', DateTime),
                         )

        users_histories = Table('Users_histories', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('user', ForeignKey('Users.id')),
                                Column('send', Integer),
                                Column('accept', Integer),
                                )

        self.metadata.create_all(self.database)

        mapper(self.Users, users)
        mapper(self.ActiveUsers, active_users)
        mapper(self.UsersLoginsHistory, users_logins_history)
        mapper(self.Contacts, contacts)
        mapper(self.UsersHistories, users_histories)

        session = sessionmaker(bind=self.database)
        self.session = scoped_session(session)

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, password, ip_address, port):
        response = self.session.query(self.Users).filter_by(username=username)

        if response.count():
            user = response.first()

            if user.password == password:
                user.last_login = datetime.now()
            else:
                raise ValueError('Wrong password!')
        else:
            user = self.Users(username, password)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user.id, ip_address, port)
        self.session.add(new_active_user)

        new_history_entry = self.UsersLoginsHistory(user.id, ip_address, port)
        self.session.add(new_history_entry)

        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.Users).filter_by(username=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def get_contacts(self, username):
        user = self.session.query(self.Users).filter_by(username=username).first()
        query = self.session.query(
            self.Contacts.contact,
            self.Contacts.connection_created_at
        ).filter_by(user=user.id)

        return query.all()

    def add_contact(self, username, contact):
        user = self.session.query(self.Users).filter_by(username=username).first()
        contact = self.session.query(self.Users).filter_by(username=contact).first()

        new_contact = self.Contacts(user.id, contact.username)
        self.session.add(new_contact)
        self.session.commit()

    def remove_contact(self, username, contact):
        user = self.session.query(self.Users).filter_by(username=username).first()
        contact = self.session.query(self.Users).filter_by(username=contact).first()

        self.session.query(self.Contacts).filter_by(user=user.id, contact=contact.username).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.Users.username,
            self.Users.last_login
        )

        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.Users.username,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.Users)

        return query.all()

    def users_logins_history_list(self, username=None):
        if not username:
            query = self.session.query(
                self.Users.username,
                self.UsersLoginsHistory.ip_address,
                self.UsersLoginsHistory.port,
                self.UsersLoginsHistory.login_time
            ).join(self.Users)

            return query.all()
        else:
            query = self.session.query(
                self.Users.username,
                self.UsersLoginsHistory.ip_address,
                self.UsersLoginsHistory.port,
                self.UsersLoginsHistory.login_time
            ).join(self.Users).filter_by(username=username)

            return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    # выполняем 'подключение' пользователя
    test_db.user_login('client_1', 'c', '192.168.1.4', 8888)
    test_db.user_login('client_2', 'c', '192.168.1.5', 7777)

    test_db.add_contact('client_1', 'client_2')
    test_db.add_contact('client_2', 'client_1')
    print(test_db.get_contacts('client_1'))
    test_db.remove_contact('client_1', 'client_2')
    print(test_db.get_contacts('client_1'))
    # выводим список кортежей - активных пользователей
    print(test_db.active_users_list())
    # выполянем 'отключение' пользователя
    test_db.user_logout('client_1')
    # выводим список активных пользователей
    print(test_db.active_users_list())
    # запрашиваем историю входов по пользователю
    print(test_db.users_logins_history_list('client_1'))
    # выводим список известных пользователей
    print(test_db.users_list())
