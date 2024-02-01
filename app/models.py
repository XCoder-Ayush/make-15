# from .extension import db

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))

#     def is_active(self):
#         return True

#     def is_authenticated(self):
#         return self.is_authenticated

#     def is_anonymous(self):
#         return False

#     def is_admin(self):
#         return self.admin

#     def get_id(self):
#         return self.id

#     def __repr__(self):
#         return f"<User {self.username}>"


# Game model
class Game:
    def __init__(self, gameId, player1Id, player2Id, moves):
        self.gameId = str(gameId)
        self.player1Id = str(player1Id)
        self.player2Id = str(player2Id)
        self.moves = [str(move) for move in moves]