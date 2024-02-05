import eventlet

eventlet.monkey_patch()

import os
import time
from flask import request
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
    PORT=os.getenv('PORT')
    print(f'PORT Is {PORT}')
    print('Before API call')
    api_url = f'http://localhost:{PORT}/api/games' 
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
    print('After API call')
    
    if response.status_code == 200:
        print('In Success')
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
    PORT=os.getenv('PORT')

    api_url = f'http://localhost:{PORT}/api/games/{room_id}'
    response = requests.get(api_url)

    if response.status_code == 200:
        game_data = response.json()

        # Check if player1Id is an empty string
        if 'player1Id' in game_data and not game_data['player1Id']:
            # Update the game with player1Id as user_id
            update_api_url = f'http://localhost:{PORT}/api/games/{room_id}'
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
            PORT=os.getenv('PORT')
            update_api_url = f'http://localhost:{PORT}/api/games/{room_id}'
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
        emit('room_joined', {'user_id': user_id, 'room_id': room_id},room=room_id,to=request.sid)
        emit('room_joined_notify', {'user_id': user_id, 'room_id': room_id},room=room_id,include_self=False)

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
    print('**************************Inside Winning Check***************************************')
    patterns = [['a', 'd', 'g'], ['b', 'e', 'h'], ['c', 'f', 'i'], ['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i'], ['a', 'e', 'i'], ['c', 'e', 'g']]
    moves = data.get('moves', [])
    if not moves:
        return
    
    wonSquare = handle_square_winning(data)
    if not wonSquare:
        # DRAW CHECK
        print('No One Won, Lets Check For Draw')
        if len(moves) == 81:
            print('Match Drawn')
            emit('draw',{'message':'Draw'}, room=data.get('gameId'))
            return
    else:
        time.sleep(1)
        print(moves)
        cell_to_number_map = {}
        for move in moves:
            cell, number_input = move
            cell_to_number_map[cell] = number_input

        print('Move Map')
        print(cell_to_number_map)

        for pattern in patterns:
            notPresentInMove = 1  
            for grid in pattern:
                for num in range(1, 10):
                    cell = grid + str(num)
                    if cell not in cell_to_number_map:
                        notPresentInMove = 0
                        break

                if not notPresentInMove:
                    break
            if notPresentInMove :
                print('Cell Complete Nahi Hua')
            else:
                print('Maybe Someone Could Win')
            
            if notPresentInMove:
                # If Player 1 Can Win:
                canPlayer1Win = 1
                for grid in pattern:
                    if data.get(f'pointsOf{grid.upper()}')[0] <= data.get(f'pointsOf{grid.upper()}')[1]:
                        canPlayer1Win=0
                        break
                
                if canPlayer1Win:
                    # Player 1 Win Event
                    print('Player 1 Wins')
                    emit('wwcd', data.get('player1Id') , room=data.get('gameId'))
                    return
                    
                canPlayer2Win = 1
                for grid in pattern:
                    if data.get(f'pointsOf{grid.upper()}')[0] >= data.get(f'pointsOf{grid.upper()}')[1]:
                        canPlayer2Win=0
                        break

                if canPlayer2Win:
                    # Player 2 Win Event
                    print('Player 2 Wins')
                    emit('wwcd', data.get('player2Id') , room=data.get('gameId'))
                    return

        print('No One Won, Lets Check For Draw')
        if len(moves) == 81:
            print('Match Drawn')
            emit('draw',{'message':'Draw'}, room=data.get('gameId'))
            return

    print('**************************Exiting Winning Check*****************************************')
    return


# @socketio.on('square_winning_check')
def handle_square_winning(data):
    moves = data.get('moves', [])
    if not moves:
        return False
    print('****************************Inside Square Win Check*****************************************')
    cell_to_number_map = {}
    for move in moves:
        cell, number_input = move
        cell_to_number_map[cell] = number_input

    print(cell_to_number_map)
    last_grid,last_input = moves[len(moves) - 1]
    last_grid=last_grid[0]
    print(last_grid)

    someoneWon=1
    for num in range(1,10):
        cell = last_grid + str(num)
        if cell not in cell_to_number_map:
            someoneWon = 0
            break    
    
    if not someoneWon:
        return False
    
    print('All Cells Filled')

    if data.get(f'pointsOf{last_grid.upper()}')[0] > data.get(f'pointsOf{last_grid.upper()}')[1]:
        print('Player 1 Won')
        emit('square_won_check',{'winner':data.get('player1Id'),'square':last_grid}, room=data.get('gameId'))
        return True
    
    if data.get(f'pointsOf{last_grid.upper()}')[0] < data.get(f'pointsOf{last_grid.upper()}')[1]:
        print('Player 2 Won')
        emit('square_won_check',{'winner':data.get('player2Id'),'square':last_grid}, room=data.get('gameId'))
        return True
        
    print('Exiting')
    return False;
# This event is triggered when a client disconnects from the server via WebSocket
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')



if __name__ == "__main__":
    app.debug = True
    print(os.getenv('PORT'))
    socketio.run(app, host='0.0.0.0', port=os.getenv('PORT'), debug=True)
