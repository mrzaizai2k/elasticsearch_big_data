# elasticsearch_big_data
This is elasticsearch project for big_data

set up lib:
```
    make install 
```

run docker 

```
docker run -d \
  --name elastic_search \
  -p 9200:9200 -p 9300:9300 \
  -e "xpack.security.enabled=false" \
  -e "discovery.type=single-node" \
  -v elasticsearch_data:/usr/share/elasticsearch/data \
  docker.elastic.co/elasticsearch/elasticsearch:8.7.0

```

Download data: https://www.kaggle.com/datasets/jrobischon/wikipedia-movie-plots?resource=download
