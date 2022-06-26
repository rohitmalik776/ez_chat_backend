from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, send, emit, rooms
from json import loads
from functools import wraps
import jwt
import datetime
import sys

from sqlalchemy import false

from utils import jsonDecode
from db_handler import Session, User

# Flask app
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'rohit@secret'

sio = SocketIO(app, cors_allowed_origins="*")


def protected_wrapper(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # For backward compatibility
        token = jsonDecode(request.data).get('token')
        # This is the better version
        # TODO: Migrate to better version.
        if(token == None):
            token = request.headers.get('Authorization')
        if(token == None):
            return jsonify('No token provided!'), 400

        try:
            jwt.decode(
                token, key=app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify('Token expired!'), 401
        except jwt.InvalidTokenError:
            return jsonify('Invalid token!'), 401
        except:
            return jsonify('Unknown error!'), 400

        return f(*args, **kwargs)
    return wrapper


# Routes

@app.route('/')
def base_route():
    return 'Application is running perfectly 👍'


@app.route('/api/auth/signup/', methods=['POST'])
def sign_up():
    # authData = loads(request.data)
    authData = jsonDecode(request.data)
    session = Session()
    newUser = User(username=authData['username'],
                   password=authData['password'])
    try:
        session.add(newUser)
        session.commit()
    except:
        session.close()
        return jsonify({'message': 'Some error occured!', 'exception': sys.exc_info()[0], 'loginStatus': 'fail'})
    session.close()
    return jsonify({'message': 'Created new user!', 'exception': 'none', 'loginStatus': 'success'})


@app.route('/api/auth/signin/', methods=['POST'])
def sign_in():
    # authData = loads(request.data)
    authData = jsonDecode(request.data)
    print(f'Login request from: {request.data}')
    session = Session()
    for user in session.query(User).all():
        if(user.username == authData['username']):
            if(user.password == authData['password']):
                token = jwt.encode(payload={'user': user.username, 'exp': datetime.datetime.now(
                ) + datetime.timedelta(hours=5)}, key=app.config['SECRET_KEY'])
                return jsonify({'jwt': token, 'loginStatus': 'success', 'username': authData['username']})
            else:
                return jsonify({'jwt': None, 'loginStatus': 'Wrong password'})
    return jsonify({'jwt': None, 'loginStatus': 'No user found'})


@app.route('/protected_route')
@protected_wrapper
def protectedRoute():
    return jsonify('You have reached protected route.')


# Websocket events

@sio.on('connect')
def connect():
    token = request.headers.get('Authorization')

    try:
        jwt.decode(
            token, key=app.config['SECRET_KEY'], algorithms=['HS256'])
    except:
        print('Denied websocket connection')
        return False

    print('Someone has Connected!')
    print(f'sid: {request.sid}')
    return True


@sio.on('disconnect')
def disconnect():
    print('Someone has disconnected!')


@sio.on('global message', namespace='/')
def handleGlobalMessageRoot(message):
    emit('global message', message, broadcast=True)


# Run app

if(__name__ == '__main__'):
    print('Starting server...')
    sio.run(app, debug=False, host='0.0.0.0', port='5000')
