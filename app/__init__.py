from flask import Flask
from flask_cors import CORS

from .views import main
from flask_pymongo import PyMongo
from .mongo_utils import init_mongo
from .mongo_instance import mongo
from dotenv import load_dotenv
import os


load_dotenv()

# mongodb+srv://ayush:J0cfX5NP0wfaEont@cluster0.zoznlvy.mongodb.net/?retryWrites=true&w=majority
# MONGO_URI="mongodb://localhost:27017/make15"

def create_app():
    app = Flask(__name__)
    # app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    CORS(app)
    # app.config["SECRET_KEY"] = "FesC9cBSuxakv9yN0vBY"
    
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')

    init_mongo(app)

    # db.init_app(app)
    # login_manager.init_app(app)
    # admin.init_app(app)
    # @login_manager.user_loader
    # def load_user(user_id):
        # return User.query.get(user_id)

    app.register_blueprint(main)
    # admin.add_view(ModelView(User, db.session))
    return app
