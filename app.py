from flask import Flask, request
from flask_socketio import SocketIO, join_room, send, emit, rooms
from os import system
from json import loads
from sqlalchemy import engine, create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Flask app
app = Flask(__name__)
app.config['SECRET_TYPE'] = 'rohit@secret'
app.config['SESSION_TYPE'] = 'filesystem'
sio = SocketIO(app, cors_allowed_origins="*")

# Sqlalchemy
engine = create_engine("mysql+pymysql://rohit:Password@localhost/ez_chat",
                       echo=False, future=True)
Base = declarative_base()

# User class


class User(Base):
    __tablename__ = 'User'

    username = Column(String(50), primary_key=True)
    password = Column(String(50))

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def __repr__(self):
        return f'username: {self.username}; password: {self.password}'


# Create the database
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/auth/signup/')
def sign_up():
    authData = loads(request.data)
    session = Session()
    newUser = User(username=authData['username'],
                   password=authData['password'])
    session.add(newUser)
    session.commit()
    session.close()

    return 'Works!'


@app.route('/api/auth/signin/')
def sign_in():
    authData = loads(request.data)
    session = Session()
    for user in session.query(User).all():
        if(user.username==authData['username']):
            if(user.password == authData['password']):
                return 'Everything fine'
            else:
                return 'Wrong password'
    return 'No user found'

@sio.on('connect')
def connect():
    print('Someone has Connected!')
    print(f'sid: {request.sid}')


@sio.on('disconnect')
def disconnect():
    print('Disconnected!')


@sio.on('global message', namespace='/')
def handleGlobalMessageRoot(message):
    print(message)
    emit('global message', message, broadcast=True)


if(__name__ == '__main__'):
    print('Starting server...')
    sio.run(app, debug=True, host='0.0.0.0', port='5000')
