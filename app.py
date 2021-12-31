from flask import Flask, request
from flask_socketio import SocketIO, join_room, send, emit, rooms
from os import system

app = Flask(__name__)
app.config['SECRET_TYPE']='rohit@secret'
app.config['SESSION_TYPE'] = 'filesystem'
sio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def hello_world():
    return 'Hello World!'

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