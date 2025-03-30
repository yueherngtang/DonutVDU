from pymongo import MongoClient
import datetime
import json

class MongoDBHandler:
    def __init__(self, db_name="donut_inference", collection_name="inference_results"):
        self.client = MongoClient("mongodb+srv://fypproject:fypproject@cluster0.huecl.mongodb.net/")  
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
        return json.dumps(results, default=str, indent=4)


if __name__ == "__main__":
    db_handler = MongoDBHandler()
    print(db_handler.get_all_results())
