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
    def __init__(self, gameId, player1Id, player2Id, moves, pointsOfA, pointsOfB, pointsOfC, pointsOfD, pointsOfE, pointsOfF, pointsOfG, pointsOfH, pointsOfI, winner):
        self.gameId = str(gameId)
        self.player1Id = str(player1Id)
        self.player2Id = str(player2Id)
        self.moves = [str(move) for move in moves]
        self.pointsOfA = [int(pointsOfA[0]), int(pointsOfA[1])]
        self.pointsOfB = [int(pointsOfB[0]), int(pointsOfB[1])]
        self.pointsOfC = [int(pointsOfC[0]), int(pointsOfC[1])]
        self.pointsOfD = [int(pointsOfD[0]), int(pointsOfD[1])]
        self.pointsOfE = [int(pointsOfE[0]), int(pointsOfE[1])]
        self.pointsOfF = [int(pointsOfF[0]), int(pointsOfF[1])]
        self.pointsOfG = [int(pointsOfG[0]), int(pointsOfG[1])]
        self.pointsOfH = [int(pointsOfH[0]), int(pointsOfH[1])]
        self.pointsOfI = [int(pointsOfI[0]), int(pointsOfI[1])]
        self.winner = winner

