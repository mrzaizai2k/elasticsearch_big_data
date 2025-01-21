# elasticsearch_big_data
This is elasticsearch project for big_data

Video demo:

<div align="center">
      <a href="https://www.youtube.com/watch?v=_TZrqAdgp3w">
         <img src="https://img.youtube.com/vi/_TZrqAdgp3w/0.jpg" style="width:80%;">
      </a>
</div>

Set up environment:
```
    make install 
```

Run Elastic Search docker

```
docker run -d \
  --name elastic_search \
  -p 9200:9200 -p 9300:9300 \
  -e "xpack.security.enabled=false" \
  -e "discovery.type=single-node" \
  -v elasticsearch_data:/usr/share/elasticsearch/data \
  docker.elastic.co/elasticsearch/elasticsearch:8.7.0

```

Run MongoDB docker (in mongodb_docker folder)

```
cd mongodb_docker
docker-compose up -d
or
docker compose -f docker-compose.yml
docker ps
```

Add index for Elastic Search

```
python add_data.py
```

Add index for MongoDB

```
python add_data_mg.py
```

Run the app:
```
    make run
    Access http://localhost:8501/ in browser
```


```
docker-compose up -d
docker ps

```

Download data: https://www.kaggle.com/datasets/jrobischon/wikipedia-movie-plots?resource=download
