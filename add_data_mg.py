import sys
sys.path.append("")

import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Connect to MongoDB with modern connection options
client = MongoClient(
    'mongodb://localhost:27017', 
    serverSelectionTimeoutMS=5000,
    server_api=ServerApi('1')
)

# Authenticate the connection
try:
    # The ismaster command is cheap and does not require auth
    client.admin.command('ismaster')
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)

db = client['movies_database']
collection = db['movies']

# Read the CSV file
df = (
    pd.read_csv("data/wiki_movie_plots_deduped.csv")
    .dropna()
    .reset_index()
)

# Drop the collection if it exists to start fresh
collection.drop()

# Prepare documents for bulk insertion
documents = []
for i, row in df.iterrows():
    doc = {
        "_id": i,
        "title": row["Title"],
        "ethnicity": row["Origin/Ethnicity"],
        "director": row["Director"],
        "cast": row["Cast"],
        "genre": row["Genre"],
        "plot": row["Plot"],
        "year": row["Release Year"],
        "wiki_page": row["Wiki Page"]
    }
    documents.append(doc)

# Bulk insert documents
if documents:
    collection.insert_many(documents)

# Create text indexes for efficient querying
# Create a text index on title, director, plot, cast, genre for better text search performance
collection.create_index([("title", "text"), 
                         ("director", "text"), 
                         ("plot", "text"), 
                         ("cast", "text"), 
                         ("genre", "text")])

# Sample query using text search instead of regex
sample_query = {
    "$text": {"$search": "jack nicholson"},  # Use $text search instead of $regex
    "$and": [
        {"director": {"$ne": "roman polanski"}}
    ]
}

# Execute the query
results = list(collection.find(sample_query))
print(f"Number of documents found: {len(results)}")

# Print total number of documents
print(f"Total documents in collection: {collection.count_documents({})}")

# Close the MongoDB connection
client.close()

print('Done')