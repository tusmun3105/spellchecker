import json
import ssl
from pymongo import MongoClient

# Replace "<password>" with your actual password
uri = "mongodb+srv://tushaar0011:Tushaar0011@cluster0.2axzrgw.mongodb.net/?retryWrites=true&w=majority"

# Name of the database and collection
database_name = 'KreolDB'
collection_name = 'user'

# Path to the JSON file containing the data to import
json_file_path = 'C:/Users/ASUS/Downloads/user.json'

# Read the JSON file
with open(json_file_path) as file:
    data = json.load(file)

# Create a new client and connect to the server
client = MongoClient(uri, ssl_cert_reqs=ssl.CERT_NONE)

# Access the specified database and collection
db = client[database_name]
collection = db[collection_name]

# Insert the data into the collection
result = collection.insert_many(data)
#print(f"Imported {len(result.inserted_ids)} documents into the collection.")

# Close the MongoDB connection
client.close()
