from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, send, emit, rooms
from json import loads
from functools import wraps
from db_handler import Session, User
import jwt
import datetime

# Flask app
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'rohit@secret'

sio = SocketIO(app, cors_allowed_origins="*")


def protected_wrapper(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = loads(request.data)['token']
        print(token)
        if(token == None):
            return 'No token provided!', 400
        
        try:
            jwt.decode(token, key=app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return 'Invalid token!', 401
        except jwt.ExpiredSignatureError:
            return 'Token expired!', 401
        except:
            return 'Unknown error!', 400

        return f(*args, **kwargs)
    return wrapper


# Routes

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
                token = jwt.encode(payload={'user': user.username, 'exp': datetime.datetime.now() + datetime.datetime(hour=24)}, key=app.config['SECRET_KEY'])
                return jsonify({'token': token})
            else:
                return 'Wrong password'
    return 'No user found'


@app.route('/protected_route')
@protected_wrapper
def protectedRoute():
    return 'You have reached protected route.'


# Websocket events

@sio.on('connect')
def connect():
    print('Someone has Connected!')
    print(f'sid: {request.sid}')


@sio.on('disconnect')
def disconnect():
    print('Someone has disconnected!')


@sio.on('global message', namespace='/')
def handleGlobalMessageRoot(message):
    print(message)
    emit('global message', message, broadcast=True)


# Run app

if(__name__ == '__main__'):
    print('Starting server...')
    sio.run(app, debug=True, host='0.0.0.0', port='5000')
