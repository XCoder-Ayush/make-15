import os
import requests
from app.__init__ import create_app
# from app.extension import db 
from flask_socketio import SocketIO, join_room, emit
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
    api_url = 'http://localhost:5000/api/games' 
    payload = {
        'gameId': room_id,
        'player1Id': user_id,
        'player2Id': '',
        'moves': [],
        'pointsOfA': [0, 0],
        'pointsOfB': [0, 0],
        'pointsOfC': [0, 0],
        'pointsOfD': [0, 0],
        'pointsOfE': [0, 0],
        'pointsOfF': [0, 0],
        'pointsOfG': [0, 0],
        'pointsOfH': [0, 0],
        'pointsOfI': [0, 0],
        'winner': ''
    }

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

        # Check if player1Id is an empty string
        if 'player1Id' in game_data and not game_data['player1Id']:
            # Update the game with player1Id as user_id
            update_api_url = f'http://localhost:5000/api/games/{room_id}'
            update_payload = {'player1Id': user_id}
            update_response = requests.put(update_api_url, json=update_payload)

            if update_response.status_code == 200:
                print(f'Player {user_id} joined the game as player1')
                return True
            else:
                print(f'Error updating game: {update_response.text}')
                return False

        # Check if player2Id is an empty string
        if 'player2Id' in game_data and not game_data['player2Id'] and game_data['player1Id'] != user_id:
            # Update the game with player2Id as user_id
            update_api_url = f'http://localhost:5000/api/games/{room_id}'
            update_payload = {'player2Id': user_id}
            update_response = requests.put(update_api_url, json=update_payload)

            if update_response.status_code == 200:
                print(f'Player {user_id} joined the game as player2')
                return True
            else:
                print(f'Error updating game: {update_response.text}')
                return False

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
        emit('room_joined', {'user_id': user_id, 'room_id': room_id},room=room_id)
    else:
        print(f'Client {user_id} is not a valid player for room {room_id}')
        emit('room_join_error', 'Invalid player for the room')
    # else:
    #     print(f'Client {user_id} is already inside a room')
    #     emit('room_join_error', 'Client is already inside a room')

def get_unique_room_id():
    return str(uuid.uuid4())


# Socket Event to register move
@socketio.on('register_move')
def handle_register_move(data):
    player_id = data.get('playerId')
    room_id = data.get('roomId')
    move = data.get('move')
    input_value = data.get('input')

    # Your logic to handle the move, update the game, etc.
    # ...

    # Broadcast the registered move to all clients in the room
    emit('get_registered_move', {'playerId': player_id, 'roomId': room_id, 'move': move, 'input': input_value}, room=room_id,include_self=False)
    

@socketio.on('winning_check')
def handle_winning_check(data):
    patterns = [['a', 'd', 'g'], ['b', 'e', 'h'], ['c', 'f', 'i'], ['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i'], ['a', 'e', 'i'], ['c', 'e', 'g']]
    moves = data.get('moves', [])
    if not moves:
        return
    
    cell_to_number_map = {}
    for move in moves:
        cell, number_input = move
        cell_to_number_map[cell] = number_input

    for pattern in patterns:
        flag = 1  
        for grid in pattern:
            for num in range(1, 10):
                cell = grid + str(num)
                if cell not in cell_to_number_map:
                    flag = 0
                    break

            if not flag:
                break
        if flag:
            # If Player 1 Can Win:
            canPlayer1Win = 1
            for grid in pattern:
                if data[f'pointsOf{grid.upper()}'][0] < data[f'pointsOf{grid.upper()}'][1]:
                    canPlayer1Win=0
                    break
             
            if canPlayer1Win:
                # Player 1 Win Event
                emit('wwcd', data.player1Id , room=data.gameId)
                
            canPlayer2Win = 1
            for grid in pattern:
                if data[f'pointsOf{grid.upper()}'][0] > data[f'pointsOf{grid.upper()}'][1]:
                    canPlayer2Win=0
                    break

            if canPlayer2Win:
                # Player 2 Win Event
                emit('wwcd', data.player2Id , room=data.gameId)

    if len(moves) == 81:
        emit('draw',{'message':'Draw'}, room=data.gameId)

    return


# This event is triggered when a client disconnects from the server via WebSocket
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')



if __name__ == "__main__":
    app.debug = True
    socketio.run(app, host='0.0.0.0', port=os.getenv('PORT'), debug=True)

