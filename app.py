import streamlit as st
from elasticsearch import Elasticsearch
from streamlit_searchbox import st_searchbox
from typing import List, Dict, Any

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

def search_movies_suggestions(query: str) -> List[str]:
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


        return suggestions
    except Exception as e:
        print("error", e)
        return []


def get_movie_details(title: str) -> Dict[str, Any]:
    """Get full movie details when a suggestion is selected."""
    if not title:
        return None

    try:
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
        return None
    except Exception as e:
        print("error", e)
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

