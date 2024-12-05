import os
import pandas as pd
from app import db, app
from sqlalchemy import text

def initialize_database():
    with app.app_context():
        db.session.execute(text('DROP TABLE IF EXISTS movie_stats'))
        db.session.execute(text('DROP TABLE IF EXISTS goldderby'))
        db.session.commit()

        movie_stats = pd.read_csv('Database/movie_stats.csv')
        goldderby = pd.read_csv('Database/goldderby.csv')


        movie_stats.to_sql('movie_stats', db.engine, index=False, if_exists='replace')
        goldderby.to_sql('goldderby', db.engine, index=False, if_exists='replace')


if __name__ == "__main__":
    initialize_database()
