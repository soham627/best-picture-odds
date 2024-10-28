import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL').replace('postgresql://', 'postgresql+psycopg://'))

goldderby_df = pd.read_csv('goldderby_data.csv')

movie_stats_df = pd.read_csv('movies_df.csv')

goldderby_df.to_sql('goldderby', engine, if_exists='replace', index=False)
movie_stats_df.to_sql('movie_stats', engine, if_exists='replace', index=False)

print("Data loaded into DB successfully.")
