from app.__init__ import create_app
from app.extension import db 
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask import request
import uuid

app = create_app()
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

# This event is triggered when a client creates a new room
@socketio.on('create_room')
def handle_create_room():
    print('Someone Connected')
    room_id = get_unique_room_id()
    join_room(room_id)
    print(f'Client created room: {room_id}')
    emit('room_created', room_id)

# This event is triggered when a client joins an existing room
@socketio.on('join_room')
def handle_join_room(room_id):
    if len(socketio.rooms[request.sid]) == 1:  # Ensure the user is not already in a room
        join_room(room_id)
        print(f'Client joined room: {room_id}')
        emit('room_joined', room_id)

def get_unique_room_id():
    return str(uuid.uuid4())

# This event is triggered when a client disconnects from the server via WebSocket
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
if __name__ == "__main__":
    app.debug = True
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
    # app.run(host="0.0.0.0", port=8000)
