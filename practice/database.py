from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from datetime import datetime
import sys
sys.path.append('../')
from common.variables import SERVER_DATABASE


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

    def __init__(self):
        self.database = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)
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

        self.metadata.create_all(self.database)

        mapper(self.Users, users)
        mapper(self.ActiveUsers, active_users)
        mapper(self.UsersLoginsHistory, users_logins_history)

        session = sessionmaker(bind=self.database)
        self.session = session()

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
            query = self.session.query(self.Users.username,
                                       self.UsersLoginsHistory.ip_address,
                                       self.UsersLoginsHistory.port,
                                       self.UsersLoginsHistory.login_time).join(self.Users).filter_by(username=username)

            return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    # выполняем 'подключение' пользователя
    test_db.user_login('client_1', 'c', '192.168.1.4', 8888)
    test_db.user_login('client_2', 'c', '192.168.1.5', 7777)
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
