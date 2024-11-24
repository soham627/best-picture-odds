import requests
from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OMDB_API_KEY")
engine = create_engine(os.getenv('DATABASE_URL').replace('postgresql://', 'postgresql+psycopg://'))

def fetch_poster_by_id(imdb_id):
    if not imdb_id:
        return None
    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and 'Poster' in data:
        return data['Poster']
    return None

movie_stats_query = "SELECT * FROM movie_stats"
movie_stats_df = pd.read_sql(movie_stats_query, engine)

movie_stats_df['Poster'] = movie_stats_df['imdb_id'].apply(fetch_poster_by_id)

movie_stats_df.to_sql('movie_stats', engine, if_exists='replace', index=False)
