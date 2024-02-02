
from flask import render_template, redirect, url_for, session, Blueprint,request,jsonify
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



@main.route('/api/games', methods=['POST'])
def create_game():
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
    games_collection = mongo.db.games
    games_collection.insert_one(new_game.__dict__)

    return jsonify({'message': 'Game created successfully'}), 200


@main.route('/api/games/<string:gameId>', methods=['GET'])
def get_game_details(gameId):
    games_collection = mongo.db.games
    game_data = games_collection.find_one({'gameId': gameId})

    if game_data:
        # Convert ObjectId to string for JSON serialization
        game_data['_id'] = str(game_data['_id'])

        # Convert MongoDB document to a dictionary and return as JSON
        return jsonify(game_data), 200
    else:
        return jsonify({'error': 'Game not found'}), 404
    


# Sample route to update a game by gameId
@main.route('/api/games/<string:gameId>', methods=['PUT'])
def update_game(gameId):
    games_collection = mongo.db.games

    # Retrieve the updated game data from the request
    updated_data = request.get_json()

    # Update the game in the MongoDB 'games' collection
    result = games_collection.update_one({'gameId': gameId}, {'$set': updated_data})

    if result.modified_count > 0:
        return jsonify({'message': 'Game updated successfully'}), 200
    else:
        return jsonify({'error': 'Game not found or no changes were made'}), 404