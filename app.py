import streamlit as st
from elasticsearch import Elasticsearch
from pymongo import MongoClient
from streamlit_searchbox import st_searchbox
from typing import List, Dict, Any
import time
from utils import timeit

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')  # No authentication needed in this case
db = client['movies_database']
collection = db['movies']

timing=0.0
timing_mongo=0.0

@timeit
def search_movies_suggestions(query: str) -> List[str]:
    global timing
    start = time.time()
    """Search for movie titles and plots with fuzzy matching and highlight matches."""
    if not query or len(query.strip()) < 2:
        return []

    try:
        response = es.search(
            index="movies",
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "plot", "director", "cast", "genre"],
                        "fuzziness": "AUTO",  # Enables fuzzy matching
                        "type": "best_fields",
                        "operator": "and"  # Ensures that all terms must match
                    }
                },
                "highlight": {
                    "fields": {
                        "title": {},
                        "plot": {},
                        "director": {},
                        "cast": {},
                        "genre": {}
                    }
                },
                "size": 10,
                "_source": ["title"]
            }
        )

        suggestions = []
        for hit in response["hits"]["hits"]:
            # Extract matched fields from the highlight section if available
            matched_fields = list(hit["highlight"].keys()) if "highlight" in hit else ["Unknown"]

            # Remove 'title' from matched fields if other fields are present
            if "title" in matched_fields and len(matched_fields) > 1:
                matched_fields.remove("title")

            # Format the matched fields for display
            matched_fields_str = ", ".join(matched_fields)
            suggestions.append(f"{hit['_source']['title']} (Matched in: {matched_fields_str})")

        stop = time.time()
        timing = (stop - start)*1000
        suggestions.insert(0, f"Search time by ES: {timing:.3f} ms")
        return suggestions
    except Exception as e:
        print("Error in search_movies_suggestions:", e)
        return []

@timeit
def search_movies_suggestions_mongo(query: str) -> List[str]:
    global timing_mongo
    start = time.time()
    """Search for movie titles and plots with keyword match and infer which fields matched."""
    if not query or len(query.strip()) < 2:
        return []
    
    try:
        suggestions = []
        
        # MongoDB text search query
        cursor = collection.find(
            {
                "$text": {"$search": query}  # Using text search
            },
            {
                "title": 1, 
                "plot": 1, 
                "director": 1, 
                "cast": 1, 
                "genre": 1,
                "score": {"$meta": "textScore"}  # Include text score for ranking
            }
        ).sort([("score", {"$meta": "textScore"})]).limit(10)  # Sort by text score and limit results
        
        # Process the results and infer matched fields
        for doc in cursor:
            matched_fields = []
            
            # Infer matched fields by checking if the query appears in each field
            for field in ["title", "plot", "director", "cast", "genre"]:
                if field in doc and query.lower() in str(doc[field]).lower():
                    matched_fields.append(field)

            # Format the matched fields for display
            matched_fields_str = ", ".join(matched_fields) if matched_fields else "Unknown"
            suggestions.append(f"{doc['title']} (Matched in: {matched_fields_str})")
        
        stop = time.time()
        timing_mongo = (stop - start) * 1000
        suggestions.insert(0, f"Search time by Mongo: {timing_mongo:.3f} ms")

        return suggestions
    except Exception as e:
        print("Error in search_movies_suggestions_mongo:", e)
        return []



def get_movie_details(title: str, elasticSearch: bool) -> Dict[str, Any]:
    """Get full movie details when a suggestion is selected."""
    if not title:
        return None

    try:
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
        return None
    except Exception as e:
        print("error", e)
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
col_show_es, col_show_mongo = st.columns(2)

if selected_movie:
    with col_show_es:
        show_movie_details(selected_movie, True)

if selected_movie_mongo:
    with col_show_mongo:
        show_movie_details(selected_movie_mongo, False)