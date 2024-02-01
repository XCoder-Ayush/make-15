import requests
from app.__init__ import create_app
# from app.extension import db 
from flask_socketio import SocketIO, join_room, leave_room, emit, send
from flask import request
import uuid

app = create_app()

socketio = SocketIO(app)

rooms={}

@socketio.on('connect')
def handle_connect():
    print('Client connected')

# This event is triggered when a client creates a new room
@socketio.on('create_room')
def handle_create_room(user_id):
    print(f'{user_id} Connected')
    room_id=get_unique_room_id();
    # Make API call to create a game
    api_url = 'http://localhost:5000/api/games'  # Replace with your API endpoint
    payload = {'gameId': room_id, 'player1Id': user_id, 'player2Id': '', 'moves': []}
    response = requests.post(api_url, json=payload)
    if response.status_code == 200:
        # Socket(Player 1) joins the room with room_id
        # join_room(room_id)
        print(f'{user_id} Created Room: {room_id}')
        # socket emits data inside the room only
        emit('room_created', room_id)
    else:
        print(f'Error creating game: {response.text}')
        emit('room_create_error', response.text)



def is_valid_player(user_id, room_id):
    # Call the API to get game details
    api_url = f'http://localhost:5000/api/games/{room_id}'
    response = requests.get(api_url)

    if response.status_code == 200:
        game_data = response.json()
        print(game_data)
        
        # Check if player2Id is an empty string
        if 'player2Id' in game_data and not game_data['player2Id']:
            return True

        # Check if the user_id matches either player1Id or player2Id
        if 'player1Id' in game_data and 'player2Id' in game_data:
            return user_id in [game_data['player1Id'], game_data['player2Id']]

    return False


@socketio.on('join_room')
def handle_join_room(data):
    room_id = data.get('roomId')
    user_id = data.get('userId')
    # print(dir(socketio))
    # if len(socketio.rooms(request.sid)) == 1:  # Ensure the user is not already in a room
        # Check if the user is a valid player for the specified room
    if is_valid_player(user_id, room_id):
        # Socket(Client) Joined The Room with room_id
        join_room(room_id)
        print(f'Client {user_id} joined room: {room_id}')
        # print('**************************************************************************')
        # print(socketio.server.manager.rooms.keys())
        # rooms = [room for room in socketio.server.manager.rooms.keys() if room != '/']
        # print(rooms)
        # now socket will emit only in the particular room_id:
        # send({'user_id': user_id, 'room_id': room_id}, to=room_id)
        emit('room_joined', {'user_id': user_id, 'room_id': room_id},broadcast=False,room=room_id)
    else:
        print(f'Client {user_id} is not a valid player for room {room_id}')
        emit('room_join_error', 'Invalid player for the room')
    # else:
    #     print(f'Client {user_id} is already inside a room')
    #     emit('room_join_error', 'Client is already inside a room')

def get_unique_room_id():
    return str(uuid.uuid4())

# This event is triggered when a client disconnects from the server via WebSocket
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')



if __name__ == "__main__":
    app.debug = True
    # with app.app_context():
    #     db.create_all()
    socketio.run(app, debug=True)
    # app.run(host="0.0.0.0", port=8000)
