import streamlit as st
<<<<<<< HEAD
from elasticsearch import Elasticsearch
=======
>>>>>>> c177075 (MongoDB edit version)
from pymongo import MongoClient
from streamlit_searchbox import st_searchbox
from typing import List, Dict, Any
import time

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')  # No authentication needed in this case
db = client['movies_database']
collection = db['movies']

# Ensure the collection has text indexes
collection.create_index([("title", "text"), 
                         ("director", "text"), 
                         ("plot", "text"), 
                         ("cast", "text"), 
                         ("genre", "text")])

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')  # No authentication needed in this case
db = client['movies_database']
collection = db['movies']

timing=0.0
timing_mongo=0.0

def search_movies_suggestions(query: str) -> List[str]:
<<<<<<< HEAD
    global timing
    start = time.time()
    """Search for movie titles and plots with fuzzy matching and highlight matches."""
=======
    """Search for movie titles and plots with keyword match and highlight which fields match."""
>>>>>>> c177075 (MongoDB edit version)
    if not query or len(query.strip()) < 2:
        return []

    try:
        # Perform text search on the fields title, plot, director, cast, and genre
        suggestions = []

        # MongoDB text search query
        cursor = collection.find(
            {
                "$text": {"$search": query}  # Using text search instead of regex
            },
            {"title": 1, "plot": 1, "director": 1, "cast": 1, "genre": 1}  # Return specific fields
        ).limit(10)  # Limit the results to 10

        # Process the results and format the matched fields
        for doc in cursor:
            matched_fields = []

            # Highlight matched fields (MongoDB text search provides this information)
            if "title" in doc:
                matched_fields.append("title")
            if "plot" in doc:
                matched_fields.append("plot")
            if "director" in doc:
                matched_fields.append("director")
            if "cast" in doc:
                matched_fields.append("cast")
            if "genre" in doc:
                matched_fields.append("genre")

            # Format the matched fields for display
<<<<<<< HEAD
            matched_fields_str = ", ".join(matched_fields)
            suggestions.append(f"{hit['_source']['title']} (Matched in: {matched_fields_str})")

        stop = time.time()
        timing = (stop - start)*1000
        suggestions.insert(0, f"Search time by ES: {timing:.3f} ms")
        return suggestions
    except Exception as e:
        print("Error in search_movies_suggestions:", e)
        return []

def search_movies_suggestions_mongo(query: str) -> List[str]:
    global timing_mongo
    start = time.time()
    """Search for movie titles and plots with keyword match and highlight which fields match."""
    if not query or len(query.strip()) < 2:
        return []
    # Perform text search on the fields title, plot, director, cast, and genre
    try:
        suggestions = []
         # MongoDB text search query
        cursor = collection.find(
            {
                "$text": {"$search": query}  # Using text search instead of regex
            },
            {"title": 1, "plot": 1, "director": 1, "cast": 1, "genre": 1}  # Return specific fields
        ).limit(10)  # Limit the results to 10
        # Process the results and format the matched fields
        for doc in cursor:
            matched_fields = []
            # Highlight matched fields (MongoDB text search provides this information)
            if "title" in doc:
                matched_fields.append("title")
            if "plot" in doc:
                matched_fields.append("plot")
            if "director" in doc:
                matched_fields.append("director")
            if "cast" in doc:
                matched_fields.append("cast")
            if "genre" in doc:
                matched_fields.append("genre")

            # Format the matched fields for display
            matched_fields_str = ", ".join(matched_fields) if matched_fields else "Unknown"
            suggestions.append(f"{doc['title']} (Matched in: {matched_fields_str})")

        stop = time.time()
        timing_mongo = (stop - start)*1000
        suggestions.insert(0, f"Search time by Mongo: {timing_mongo:.3f} ms")

        return suggestions
    except Exception as e:
        print("Error in search_movies_suggestions_mongo:", e)
        return []


def get_movie_details(title: str, elasticSearch: bool) -> Dict[str, Any]:
=======
            matched_fields_str = ", ".join(matched_fields) if matched_fields else "Unknown"
            suggestions.append(f"{doc['title']} (Matched in: {matched_fields_str})")

        return suggestions
    except Exception as e:
        print("Error:", e)
        return []

def get_movie_details(title: str) -> Dict[str, Any]:
>>>>>>> c177075 (MongoDB edit version)
    """Get full movie details when a suggestion is selected."""
    if not title:
        return None

    try:
<<<<<<< HEAD
        if (elasticSearch):
            response = es.search(
                index="movies",
                body={
                    "query": {
                        "match": {
                            "title": title
                        }
                    },
                    "size": 1,
                    "_source": ["title", "director", "cast", "genre", "year", "plot"]
                }
            )

            if response["hits"]["hits"]:
                return response["hits"]["hits"][0]["_source"]
        else:
             # MongoDB query to fetch movie details by title
            movie = collection.find_one({"title": title}, {
                "title": 1, "director": 1, "cast": 1, "genre": 1, "year": 1, "plot": 1
            })

            if movie:
                return movie     
=======
        # MongoDB query to fetch movie details by title
        movie = collection.find_one({"title": title}, {
            "title": 1, "director": 1, "cast": 1, "genre": 1, "year": 1, "plot": 1
        })

        if movie:
            return movie
>>>>>>> c177075 (MongoDB edit version)
        return None
    except Exception as e:
        print("Error:", e)
        st.error(f"Error fetching movie details: {str(e)}")
        return None

def show_movie_details(selected_movie: str, elasticSearch: bool):
    if not selected_movie:
        return None

    if (selected_movie.find("Search time") == -1):
            # Extract only the title (removing the "Matched in" part)
            movie_title = selected_movie.split(" (Matched in:")[0].strip()
            movie_info = get_movie_details(movie_title, elasticSearch)
            if movie_info:
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 5px; background-color: #f9f9f9; color: #000;">
                    <h2 style="color: #000;">🎬 {movie_info['title']} ({movie_info['year']})</h2>
                    <p><strong>🎥 Director:</strong> {movie_info['director']}</p>
                    <p><strong>👥 Cast:</strong> {movie_info['cast']}</p>
                    <p><strong>🎭 Genre:</strong> {movie_info['genre']}</p>
                    <p><strong>📖 Plot:</strong> {movie_info['plot']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 5px; background-color: #f9f9f9; color: #000;">
                    <h2 style="color: #000;">🎬 Error: (Don't select search time)</h2>
                </div>
                """, unsafe_allow_html=True)

# Streamlit App
st.title("🎥 Movie Search Engine")
st.write("Start typing to search for movies by title, plot, director, cast, or genre.")


# Search boxes
col_search_es, col_search_mongo = st.columns(2)

with col_search_es:
    selected_movie = st_searchbox(
        search_movies_suggestions,
        key="movie_searchbox",
        placeholder="🔍 Search by Elastic Search",
        clear_on_submit=True
    )

with col_search_mongo:
    selected_movie_mongo = st_searchbox(
        search_movies_suggestions_mongo,
        key="movie_searchbox_1",
        placeholder="🔍 Search by MongoDB",
        clear_on_submit=True
    )

# Display movie details when a suggestion is selected
<<<<<<< HEAD
col_show_es, col_show_mongo = st.columns(2)

if selected_movie:
    with col_show_es:
        show_movie_details(selected_movie, True)

if selected_movie_mongo:
    with col_show_mongo:
        show_movie_details(selected_movie_mongo, False)
=======
if selected_movie:
    # Extract only the title (removing the "Matched in" part)
    movie_title = selected_movie.split(" (Matched in:")[0].strip()
    movie_info = get_movie_details(movie_title)
    if movie_info:
        st.markdown(f"""
        <div style="border: 1px solid #ddd; padding: 20px; border-radius: 5px; background-color: #f9f9f9; color: #000;">
            <h2 style="color: #000;">🎬 {movie_info['title']} ({movie_info['year']})</h2>
            <p><strong>🎥 Director:</strong> {movie_info['director']}</p>
            <p><strong>👥 Cast:</strong> {movie_info['cast']}</p>
            <p><strong>🎭 Genre:</strong> {movie_info['genre']}</p>
            <p><strong>📖 Plot:</strong> {movie_info['plot']}</p>
        </div>
        """, unsafe_allow_html=True)
>>>>>>> c177075 (MongoDB edit version)
