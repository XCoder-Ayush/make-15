from .mongo_instance import mongo
import os

def init_mongo(app):
    try:
        with app.app_context():
            mongo_uri = os.getenv('MONGO_URI')
            port = os.getenv('PORT')
            print(f'Here Is The Port {port}')
            mongo.init_app(app, uri=mongo_uri)

            if mongo.db is not None:
                print("Connected to MongoDB")
                print(mongo.db)
            else:
                print("Not Connected To DB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise
