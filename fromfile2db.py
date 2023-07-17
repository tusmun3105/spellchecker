from pymongo import MongoClient

# Database connection details
connection_string = "mongodb://localhost:27017"
database_name = "KreolDB"
collection_name = "dictionary"

# Connect to the database
client = MongoClient(connection_string)
db = client[database_name]
collection = db[collection_name]

# Empty the "dictionary" collection
collection.delete_many({})

# Read lines from the file and store in the collection
with open("static/sorted_words.txt", "r") as file:
    lines = file.readlines()

    word_set = set()  # Set to store unique words

    for i, line in enumerate(lines):
        word = line.strip()

        # Skip if the word has already been inserted
        if word in word_set:
            continue

        word_set.add(word)  # Add word to the set

        document = {"_id": i + 1, "word": word}
        collection.insert_one(document)
