import streamlit as st
from pymongo import MongoClient
from streamlit_searchbox import st_searchbox
from typing import List, Dict, Any

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

def search_movies_suggestions(query: str) -> List[str]:
    """Search for movie titles and plots with keyword match and highlight which fields match."""
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
            matched_fields_str = ", ".join(matched_fields) if matched_fields else "Unknown"
            suggestions.append(f"{doc['title']} (Matched in: {matched_fields_str})")

        return suggestions
    except Exception as e:
        print("Error:", e)
        return []

def get_movie_details(title: str) -> Dict[str, Any]:
    """Get full movie details when a suggestion is selected."""
    if not title:
        return None

    try:
        # MongoDB query to fetch movie details by title
        movie = collection.find_one({"title": title}, {
            "title": 1, "director": 1, "cast": 1, "genre": 1, "year": 1, "plot": 1
        })

        if movie:
            return movie
        return None
    except Exception as e:
        print("Error:", e)
        st.error(f"Error fetching movie details: {str(e)}")
        return None

# Streamlit App
st.title("🎥 Movie Search Engine")
st.write("Start typing to search for movies by title, plot, director, cast, or genre.")

# Real-time search box with suggestions
selected_movie = st_searchbox(
    search_movies_suggestions,
    key="movie_searchbox",
    placeholder="🔍 Search movies by title, plot, cast, director, or genre...",
    clear_on_submit=True
)

# Display movie details when a suggestion is selected
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
