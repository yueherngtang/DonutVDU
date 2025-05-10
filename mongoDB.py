from typing import Union
from pymongo import MongoClient
import datetime
import json
import bcrypt

def test_mongo_connection(uri: str) -> bool:
    try:
        client = MongoClient(uri)
        client.admin.command('ping')
        return True
    except Exception as e:
        return False

class MongoDBHandlerUser:
    def __init__(self, db_name, collection_name, mongo_client = None):
        self.client = MongoClient(mongo_client)  
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def save_inference_result(self, image_name, task_name, prediction):
        """Save structured JSON inference result to MongoDB."""
        document = {
            "image_name": image_name,
            "task_name": task_name,
            "output_data": prediction,  # Store the full JSON output
            "timestamp": datetime.datetime.utcnow()
        }
        self.collection.insert_one(document)
        print(f"Saved to MongoDB:\n{json.dumps(document, indent=4, default=str)}")

    def get_all_results(self):
        """Retrieve all stored inference results."""
        results = list(self.collection.find({}, {"_id": 0}))  # Exclude MongoDB ObjectId
        return flatten_rows(results)
    
    def search_results(self, keys : list[str], values : list[str|int|float]):
        assert len(keys) == len(values)
        query = {}
        for key, value in zip(keys, values):
            query[f"output_data.{key}"] = str(value)
        print(query)

        doc = self.collection.find(query)
        print(doc)
        return flatten_rows(doc)
        
    


class MongoDBHandlerLogin:
    def __init__(self, db_name="donut_login", collection_name="user"):
        self.client = MongoClient("mongodb+srv://donut_login:donut_mds13@donutlogin.jtd83h6.mongodb.net/?retryWrites=true&w=majority&appName=donutlogin") 
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        
        self.db = self.client[db_name]

        self.collection = self.db[collection_name]
        self.collection.create_index("username", unique=True)
    
    def add_user(self, username, password, dbname, collection_name, mongo_client):
        if self.collection.find_one({"username": username}):
            return False

        # Prepare the user document
        user_data = {
            "username": username,
            "password": password,
            "db_name": dbname,
            "collection_name": collection_name,
            "mongo_client": mongo_client
        }

        self.collection.insert_one(user_data)
        return True

    def get_user(self,username):
        user = self.collection.find_one({"username": username})
        return user

    def login(self,username, password):
        user = self.collection.find_one({"username": username})
        if user:
            if self.check_password(password,user['password']):
                return True
        return False

    def check_password(self, password, hashed_password):
        return bcrypt.checkpw(password.encode(), hashed_password)
    
    def change_password(self, username, password):
        result = self.collection.update_one(
            {"username": username},
            {"$set": {"password": password}}
        )

        if result:
            return True
        return False
    
    def change_db_config(self, username, new_db_name, new_collection_name, new_mongo_client):
        result = self.collection.update_one(
            {"username": username},
            {"$set": {
                    "db_name": new_db_name,
                    "collection_name": new_collection_name,
                    "mongo_client": new_mongo_client
                }
            }
        )

        return result.matched_count > 0

def flatten_rows(results: Union[list, dict]):
    flat_rows = []
    for entry in results:
        if isinstance(entry["output_data"], list):
            entry = entry["output_data"][0]
        else:
            entry = entry["output_data"]
        base = {
            "merchant": None,
            "date": None,
            "recipient": None,
            "subtotal_price" : None,
            "total_price": None,
            }
        for key in base.keys():
            if key in entry:
                base[key] = str(entry[key])

        if "menu" in entry:
            for i, item in enumerate(entry["menu"]):
                for key, val in item.items():
                    base[f"menu_{i+1}_{key}"] = str(val)
        flat_rows.append(base)
    return flat_rows

if __name__ == "__main__":
    db_handler = MongoDBHandlerLogin()
