import streamlit as st
from elasticsearch import Elasticsearch
from streamlit_searchbox import st_searchbox
from typing import List, Dict, Any

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

def search_movies_suggestions(query: str) -> List[str]:
    """Search for movie titles and plots with fuzzy matching."""
    if not query or len(query.strip()) < 2:
        return []

    try:
        response = es.search(
            index="movies",
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "plot"],
                        "fuzziness": "AUTO",  # Enables fuzzy matching
                        "type": "best_fields"
                    }
                },
                "size": 5,
                "_source": ["title"]
            }
        )
        
        return [hit["_source"]["title"] for hit in response["hits"]["hits"]]
    except Exception as e:
        st.error(f"Search error: {str(e)}")
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
        st.error(f"Error fetching movie details: {str(e)}")
        return None

# Streamlit App
st.title("Movie Search Engine")
st.write("Start typing to search movies by title or plot")

# Create containers for results
movie_details_container = st.container()

# Real-time search box with suggestions
selected_movie = st_searchbox(
    search_movies_suggestions,
    key="movie_searchbox",
    placeholder="Search movies...",
    clear_on_submit=False
)

# Display movie details when a suggestion is selected
if selected_movie:
    with movie_details_container:
        movie_info = get_movie_details(selected_movie)
        if movie_info:
            st.markdown(f"""
### {movie_info['title']} ({movie_info['year']})
**Director:** {movie_info['director']}  
**Cast:** {movie_info['cast']}  
**Genre:** {movie_info['genre']}  
**Plot:** {movie_info['plot']}
---
""")
