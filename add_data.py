import sys
sys.path.append("") 

import pandas as pd

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


es = Elasticsearch("http://localhost:9200")
es.info().body


df = (
    pd.read_csv("data/wiki_movie_plots_deduped.csv")
    .dropna()
    .reset_index()
)

mappings = {
        "properties": {
            "title": {"type": "text", "analyzer": "english"},
            "ethnicity": {"type": "text", "analyzer": "standard"},
            "director": {"type": "text", "analyzer": "standard"},
            "cast": {"type": "text", "analyzer": "standard"},
            "genre": {"type": "text", "analyzer": "standard"},
            "plot": {"type": "text", "analyzer": "english"},
            "year": {"type": "integer"},
            "wiki_page": {"type": "keyword"}
    }
}

es.indices.create(index="movies", mappings=mappings)


for i, row in df.iterrows():
    doc = {
        "title": row["Title"],
        "ethnicity": row["Origin/Ethnicity"],
        "director": row["Director"],
        "cast": row["Cast"],
        "genre": row["Genre"],
        "plot": row["Plot"],
        "year": row["Release Year"],
        "wiki_page": row["Wiki Page"]
    }

    es.index(index="movies", id=i, document=doc)


bulk_data = []
for i,row in df.iterrows():
    bulk_data.append(
        {
            "_index": "movies",
            "_id": i,
            "_source": {
                "title": row["Title"],
                "ethnicity": row["Origin/Ethnicity"],
                "director": row["Director"],
                "cast": row["Cast"],
                "genre": row["Genre"],
                "plot": row["Plot"],
                "year": row["Release Year"],
                "wiki_page": row["Wiki Page"],
            }
        }
    )
bulk(es, bulk_data)

es.indices.refresh(index="movies")
es.cat.count(index="movies", format="json")

resp = es.search(
    index="movies",
    query={
            "bool": {
                "must": {
                    "match_phrase": {
                        "cast": "jack nicholson",
                    }
                },
                "filter": {"bool": {"must_not": {"match_phrase": {"director": "roman polanski"}}}},
            },
        },
)
print('res', resp.body)
