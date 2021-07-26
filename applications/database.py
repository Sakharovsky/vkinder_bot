import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime as dt
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from config import *

base = declarative_base()
host = f'{DB_DRIVER}://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = sq.create_engine(host)
sess = sq.orm.sessionmaker()
session = sess(bind=engine)

user_to_client = sq.Table('user_to_client', base.metadata,
    sq.Column('user_id', sq.ForeignKey('users.id'), primary_key=True),
    sq.Column('client_id', sq.ForeignKey('clients.id'), primary_key=True))

user_to_search = sq.Table('user_to_search', base.metadata,
    sq.Column('user_id', sq.ForeignKey('users.id'), primary_key=True),
    sq.Column('search_id', sq.ForeignKey('searches.id'), primary_key=True))

class users(base):
    __tablename__ = 'users'

    id = sq.Column(sq.Integer, primary_key=True)
    client = sq.orm.relationship('clients', secondary=user_to_client, back_populates='user')
    search = sq.orm.relationship('searches', secondary=user_to_search,back_populates='user')
    name = sq.Column(sq.String, nullable=False)
    lastname = sq.Column(sq.String, nullable=False)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    token = sq.Column(sq.String)
    updated = sq.Column(sq.TIMESTAMP, nullable=False)

    def __init__(self, name, lastname, vk_id):
        self.name = name
        self.lastname = lastname
        self.vk_id = vk_id
        self.updated = dt.now()
    
    def __repr__(self):
        return f'id: {self.id}, name: {self.name}, lastname: {self.lastname}, vk_id: {self.vk_id}, token: {self.token}, updated: {self.updated}'

class clients(base):
    __tablename__ = 'clients'

    id = sq.Column(sq.Integer, primary_key=True)
    user = sq.orm.relationship('users', secondary=user_to_client, back_populates='client')
    search = sq.orm.relationship('searches', backref='clients')
    name = sq.Column(sq.String, nullable=False)
    lastname = sq.Column(sq.String, nullable=False)
    vk_id = sq.Column(sq.Integer, nullable=False)
    age = sq.Column(sq.Numeric, sq.CheckConstraint('age > 0 AND age < 99'))
    city = sq.Column(sq.Numeric)
    status = sq.Column(sq.Numeric)
    sex_id = sq.Column(sq.Numeric)
    chosen = sq.Column(sq.Numeric, sq.CheckConstraint('chosen = 0 OR chosen = 1'), nullable=False)
    search_list = sq.Column(sq.JSON)
    updated = sq.Column(sq.TIMESTAMP, nullable=False)

    def __init__(self, vk_id, name, lastname, age, city, status, sex_id):
        self.vk_id = vk_id
        self.name = name
        self.lastname = lastname
        self.age = age
        self.city = city
        self.status = status
        self.sex_id = sex_id
        self.chosen = 1
        self.updated = dt.now()
    
    def __repr__(self):
        return f'id: {self.id}, name: {self.name}, lastname: {self.lastname}, vk_id: {self.vk_id}, age: {self.age}, city: {self.city}, sex_id: {self.sex_id}, chosen: {self.chosen}, updated: {self.updated}'

class searches(base):
    __tablename__ = 'searches'

    id = sq.Column(sq.Integer, primary_key=True)
    user = sq.orm.relationship('users', secondary=user_to_search, back_populates='search')
    client = sq.Column(sq.Integer, sq.ForeignKey('clients.id'))
    name = sq.Column(sq.String, nullable=False)
    lastname = sq.Column(sq.String, nullable=False)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    rating_id = sq.Column(sq.Integer)
    updated = sq.Column(sq.TIMESTAMP, nullable=False)

    def __init__(self, vk_id, name, lastname):
        self.vk_id = vk_id
        self.name = name
        self.lastname = lastname
        self.updated = dt.now()
    
    def __repr__(self):
        return f'id: {self.id}, name: {self.name}, lastname: {self.lastname}, vk_id: {self.vk_id}, rating_id: {self.rating_id}'

def build():
    base.metadata.create_all(engine)

def test_db():

    ed_user = users(vk_id = 1222333, name = 'Ed', lastname = 'Lebovski')
    eddy_client = clients(vk_id = 9999999, name = 'Eddy', lastname = 'Lebovski')
    galya_search = searches(vk_id = 1000000, name = 'Galya', lastname = 'Nebovski')

    session.add(ed_user)
    session.add(eddy_client)
    session.add(galya_search)

    ed_user.client.append(eddy_client)
    ed_user.search.append(galya_search)


    # ed = session.query(users).filter_by(name='Ed').first()
    # galya = session.query(searches).filter_by(name='Galya').first()
    # eddy = session.query(clients).filter_by(name='Eddy').first()

    session.commit()

def get_user_info(vk_id):
    session = sq.orm.sessionmaker(bind=engine)
    with session() as session:
        user = session.query(users).filter_by(vk_id=vk_id).first()
    return user

def upd_token(vk_id, token):
    session = sq.orm.sessionmaker(bind=engine)
    with session() as session:
        user = session.query(users).filter_by(vk_id=vk_id).first()
        user.token = token
        session.commit()

def upd_client(vk_id, age=None, city=None, status=None, sex=None):
    session = sq.orm.sessionmaker(bind=engine)
    with session() as session:
        user = session.query(users).filter_by(vk_id=vk_id).first()
        clients = user.client
        for client in clients:
            if client.chosen == 1:
                if age != None:
                    client.age = age
                elif city != None:
                    client.city = city
                elif status != None:
                    client.status = status
                elif sex != None:
                    client.sex_id = sex
                session.commit()

def get_user_client(vk_id):
    session = sq.orm.sessionmaker(bind=engine)
    with session() as session:
        user = session.query(users).filter_by(vk_id=vk_id).first()
        clients = user.client
        for client in clients:
            if client.chosen == 1:
                return client

def conn_user_client(vk_id, client):
    session = sq.orm.sessionmaker(bind=engine)
    with session() as session:
        user = session.query(users).filter_by(vk_id=vk_id).first()
        user.client.append(client)
        session.commit()

def to_db(object):
    sess = sq.orm.sessionmaker()
    session = sess(bind=engine)
    session.add(object)
    session.commit()
    return True

if __name__ == '__main__':

    # client_info = get_user_client(1)
    # print(client_info[0].client)
    # client = get_user_client(1)
    # print(client.name)

    # user2 = users('Viktor', 'Bobikov', '2223334', '1')
    # print(to_db(user2))
    
    # print(get_user_client(1222333))
    
    # upd_token(154873356, None)

    """Сетап"""
    # build()

    pass