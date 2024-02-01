# mongo_utils.py
from flask import Flask
from .mongo_instance import mongo
from flask_pymongo import PyMongo

def init_mongo(app):
    try:
        with app.app_context():
            mongo.init_app(app)
            mongo.cx.server_info()
            print("Connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
