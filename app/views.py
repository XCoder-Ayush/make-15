from flask import make_response, render_template, redirect, url_for, session, Blueprint,request,jsonify
from flask_login import login_required, current_user
from .models import Game
from .mongo_instance import mongo
from bson import ObjectId

main = Blueprint("main", __name__)


# @main.route("/login", methods=["GET", "POST"])
# def login():
#     msg = ""
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         user = User.query.filter_by(username=username).first()
#         if user:
#             if user.password == password:
#                 login_user(user)
#                 return redirect(url_for("main.home"))
#             else:
#                 flash("username or password incorrect")
#     return render_template("login.html", msg=msg)


# @main.route("/logout")
# def logout():
#     # Remove session data, this will log the user out
#     logout_user()
#     # Redirect to login page
#     return redirect(url_for("main.login"))


# @main.route("/register", methods=["GET", "POST"])
# def register():
#     # Output message if something goes wrong...
#     msg = ""
#     # Check if "username", "password" and "email" POST requests exist (user submitted form)
#     if (
#         request.method == "POST"
#         and "username" in request.form
#         and "password" in request.form
#     ):
#         # Create variables for easy access
#         username = request.form["username"]
#         password = request.form["password"]
#         # Check if account exists in DB
#         account = User.query.filter_by(username=username).first()
#         # If account exists show error and validation checks
#         if account:
#             msg = "Account already exists!"
#         elif not re.match(r"[A-Za-z0-9]+", username):
#             msg = "Username must contain only characters and numbers!"
#         elif not username or not password:
#             msg = "Please fill out the form!"
#         else:
#             user = User(username=username, password=password)
#             db.session.add(user)
#             db.session.commit()
#             msg = "You have successfully registered!"
#             return redirect(url_for("main.login"))
#     return render_template("register.html", msg=msg)


# @main.route("/")
# def home():
#     # Check if user is loggedin
#     if "_user_id" in session:
#         # User is loggedin show them the home page
#         return render_template(
#             "home.html", username=User.query.filter_by(id=session["_user_id"]).first()
#         )
#     # User is not loggedin redirect to login page
#     return redirect(url_for("main.login"))


@main.route("/")
def home():
    return render_template("visit.html")

@main.route('/game/<string:room_id>', methods=['GET'])
def sendIndex(room_id):
    return render_template("index.html",room_id=room_id)


# @main.route("/profile")
# @login_required
# def profile():
#     # Check if user is loggedin
#     if current_user.is_authenticated:
#         # We need all the account info for the user so we can display it on the profile page

#         # Show the profile page with account info
#         return render_template(
#             "profile.html", account=User.query.filter_by(id=session["_user_id"]).first()
#         )
#     # User is not loggedin redirect to login page
#     return redirect(url_for("main.login"))


@main.route('/api/health', methods=['GET'])
def health_check():
    response = {'status': 'success', 'message': 'Health check passed'}
    return jsonify(response)

@main.route('/api/games', methods=['POST'])
def create_game():
    print('IN CREATE GAME API')
    data = request.get_json()

    # Extract fields from the JSON data
    gameId = data.get('gameId')
    player1Id = data.get('player1Id')
    player2Id = data.get('player2Id')
    moves = data.get('moves', [])

    # Create a new game object
    new_game = Game(
        gameId=gameId,
        player1Id=player1Id,
        player2Id=player2Id,
        moves=moves,
        pointsOfA=[0, 0],
        pointsOfB=[0, 0],
        pointsOfC=[0, 0],
        pointsOfD=[0, 0],
        pointsOfE=[0, 0],
        pointsOfF=[0, 0],
        pointsOfG=[0, 0],
        pointsOfH=[0, 0],
        pointsOfI=[0, 0],
        winner=''
    )

    # Insert the game document into the MongoDB 'games' collection
    print('Before Saving To DB')
    print(mongo.db)
    games_collection = mongo.db.games
    print(games_collection)
    games_collection.insert_one(new_game.__dict__)
    print('After Saving To DB')

    return jsonify({'message': 'Game created successfully'}), 200


@main.route('/api/games/<string:gameId>', methods=['GET'])
def get_game_details(gameId):
    games_collection = mongo.db.games
    game_data = games_collection.find_one({'gameId': gameId})

    if game_data:
        # Convert ObjectId to string for JSON serialization
        game_data['_id'] = str(game_data['_id'])
        # Convert MongoDB document to a dictionary
        game_dict = dict(game_data)
        # Return the dictionary as JSON with a 200 status code
        return make_response(jsonify(game_dict), 200)
    else:
        # Return a JSON response with a 404 status code
        return make_response(jsonify({'error': 'Game not found'}), 404)
    

# Sample route to update a game by gameId
@main.route('/api/games/<string:gameId>', methods=['PUT'])
def update_game(gameId):
    games_collection = mongo.db.games

    # Retrieve the updated game data from the request
    updated_data = request.get_json()

    # Score Calculation/Updates 
    final_updated_data = scoreCalculation(updated_data)
    final_updated_data.pop('_id', None)


    # Winning Check:
    # winningCheck(final_updated_data); 
    # Can be done as a Webhook in future:

    # Update the game in the MongoDB 'games' collection

    result = games_collection.update_one({'gameId': gameId}, {'$set': final_updated_data})

    if result.modified_count > 0:
        return jsonify({'message': 'Game updated successfully'}), 200
    else:
        return jsonify({'error': 'Game not found or no changes were made'}), 404
    

def scoreCalculation(updated_data):
    moves = updated_data.get('moves', [])
    if not moves:
        return updated_data
    
    last_move = updated_data.get('moves', [])[-1]
    cell, numberInput = last_move
    patterns = [[1, 4, 7], [2, 5, 8], [3, 6, 9], [1, 2, 3], [4, 5, 6], [7, 8, 9], [1, 5, 9], [3, 5, 7]]

    grid = cell[0]
    associatedNumber = int(cell[1])
    
    cell_to_number_map = {}
    for move in moves:
        cell, number_input = move
        cell_to_number_map[cell] = number_input
    
    score=0

    for pattern in patterns:
        flag = 1  
        pattern_sum = 0
        if associatedNumber in pattern:
            for num in pattern:
                cell = grid + str(num)
                
                if cell not in cell_to_number_map:
                    flag = 0
                    break

                pattern_sum += cell_to_number_map[cell]

            if flag:
                if pattern_sum == 15:
                    score += 1

    print('***********************************************************************')
    print(updated_data)

    if len(moves) % 2 == 1:
        updated_data[f'pointsOf{grid.upper()}'][0] += score
    else:
        updated_data[f'pointsOf{grid.upper()}'][1] += score

    return updated_data

@main.route("/api/moves", methods=['POST'])
def get_valid_moves_in_cell():
    data = request.get_json()

    print('**************************Inside Get Valid Moves*****************************')
    print(data)
    gameId=data.get('gameId')
    current_cell=data.get('currentCell')

    game_details=get_game_details(gameId)
    moves=game_details.json['moves']
    # moves = game_details.get('moves', [])    
    print(moves)

    grid=current_cell[0]
    cell_to_number_map = {}
    for move in moves:
        cell, number_input = move
        cell_to_number_map[cell] = number_input    

    print(cell_to_number_map)

    moves_allowed=[1,2,3,4,5,6,7,8,9]


    # Distinct Condition Check:

    for num in range(1,10):
        cell = grid + str(num)
        if cell in cell_to_number_map:
            moves_allowed.remove(cell_to_number_map[cell])

    print('*************************After Distinct***************************')
    print(moves_allowed)

    # Prev 10 Moves Condition Check

    player_1_moves = []
    player_2_moves = []

    for index, move in enumerate(moves):
        cell, number_input = move
        if index % 2 == 0:
            player_1_moves.append(number_input)
        else:
            player_2_moves.append(number_input)

    # X Y 1 2 3 4 5 6 7 8 9 10 [11th Is Okay]
    # X+Y>=15

    further_filter=False

    if len(moves)%2==0:
        for i in range(len(player_1_moves) - 1, 0, -1):
            current_sum = player_1_moves[i] + player_1_moves[i - 1]
            if current_sum >= 15:
                remaining_moves = player_1_moves[i+1:]
                if len(remaining_moves) < 10:
                    further_filter = True
                    break
                if further_filter:
                    break
    else:
        for i in range(len(player_2_moves) - 1, 0, -1):
            current_sum = player_2_moves[i] + player_2_moves[i - 1]
            if current_sum >= 15:
                remaining_moves = player_2_moves[i+1:]
                if len(remaining_moves) < 10:
                    further_filter = True
                    break
                if further_filter:
                    break        
    

    if further_filter:
        last_element_player_1_moves = player_1_moves[-1]
        last_element_player_2_moves = player_2_moves[-1]
        if len(moves)%2==0:
            for num in range(len(moves_allowed) - 1, -1, -1):
                current_number = moves_allowed[num]
                if last_element_player_1_moves + current_number >= 15:
                    moves_allowed.pop(num)
        else:
            for num in range(len(moves_allowed) - 1, -1, -1):
                current_number = moves_allowed[num]
                if last_element_player_2_moves + current_number >= 15:
                    moves_allowed.pop(num)                
        
    print('************************After All Updation****************************')
    print(moves_allowed)

    return jsonify(moves_allowed), 200