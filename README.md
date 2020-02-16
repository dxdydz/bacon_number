# Bacon Number

Flask & Redis based API for calculating the degrees of separation between a given actor and Kevin Bacon. Cast data is from [the movies dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset) collected from TMDB.

## Requirements

* Flask
* Redis

## Building or loading the Redis database

### Build database from scratch

`load_movie_data.py` is a script that reads in the csv data files with movie and cast information from `/data` and propagates the Redis database. **The script will add the keys to the `localhost` Redis server if one is running, so make sure that's what you want to do.** If there is no conflict, and you want to build the database from scratch, (re)start the redis server and make sure it's empty:

    sudo service redis-server restart
    redis-cli FLUSHALL

Place `credits.csv` and `movies_metadata.csv` from [the movies dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset) in `/data` and run the database generation script:

    python load_movie_data.py

### Load pre-built database

To avoid re-building database, you can instead point a redis-server instance to a prebuilt db at `data/dump.rdb`:

    redis-server --dir /path/to/data/dump.rdb

## Running & Interfacting with the Flask Server

With the Redis database running, start the Flask server with:

    python app.py

The end-point `/bacon` returns the bacon degrees of separation. For example:

    curl -i -X GET http://localhost:5000/bacon?name=Patrick%20Stewart

Returns:

    {
    "bacon_number": 2,
    "chain": [
        {
        "actor_1": "Patrick Stewart",
        "actor_2": "Chevy Chase",
        "movie": "L.A. Story"
        },
        {
        "actor_1": "Chevy Chase",
        "actor_2": "Kevin Bacon",
        "movie": "Drunk Stoned Brilliant Dead: The Story of the National Lampoon"
        }
    ]
    }

