from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, create_engine
import os
from dotenv import load_dotenv
import pandas as pd
import requests
from datetime import datetime, timedelta
import json

load_dotenv()

app = Flask(__name__)
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')

# configuring database URI to use psycopg instead of psycopg2
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgresql://"):
    uri = uri.replace("postgresql://", 'postgresql+psycopg://', 1)
else:
    uri = "sqlite:///local.db"

app.config['SQLALCHEMY_DATABASE_URI'] = uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

engine = create_engine(os.getenv('DATABASE_URL').replace('postgresql://', 'postgresql+psycopg://'))

omdb_api_key = os.environ.get('OMDB_API_KEY')

def get_news_for_movie(movie_name):
    # check db for existing articles
    query = text("SELECT articles, last_updated FROM movie_news WHERE movie_name = :movie_name")
    with engine.connect() as conn:
        result = conn.execute(query, {"movie_name": movie_name}).fetchone()

    if result:
        articles, last_updated = result
        if last_updated and (datetime.now() - last_updated) < timedelta(days=1):  # Update daily
            return json.loads(articles)

    # Otherwise get from News API
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f'{movie_name} movie',
        "apiKey": os.getenv("NEWS_API_KEY"),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        raw_articles = response.json().get("articles", [])
        relevant_articles = [
            {
                "title": article["title"],
                "url": article["url"],
                "description": article.get("description", "No description available."),
                "publishedAt": datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
            }
            for article in raw_articles
            if movie_name.lower() in article["title"].lower()
        ]

        simplified_articles = relevant_articles[:3]

        query_add = """
            INSERT INTO movie_news (movie_name, articles, last_updated)
            VALUES (:movie_name, :articles, :last_updated)
            ON CONFLICT (movie_name)
            DO UPDATE SET articles = EXCLUDED.articles, last_updated = EXCLUDED.last_updated
        """
        with engine.connect() as conn:
            conn.execute(
                text(query_add),
                {
                    "movie_name": movie_name,
                    "articles": json.dumps(simplified_articles),
                    "last_updated": datetime.now()
                }
            )
        return simplified_articles
    else:
        return []

@app.route('/')
def homepage():
    # Finds the top 3 movies based on Goldderby all star users' votes
    query = """
        SELECT ms."Movie Name", ms."Poster", gd.pct_vote_star24, gd.betting_pct
        FROM movie_stats ms
        JOIN goldderby gd ON ms."Movie Name" = gd."Movie Name"
        WHERE gd."Date" = (SELECT MAX("Date") FROM goldderby)
        ORDER BY gd.pct_vote_star24 DESC
        LIMIT 3
    """
    top_movies = pd.read_sql(text(query), db.engine)

    # converts to dictionary which is then used in the homepage template
    top_movies_data = top_movies.to_dict(orient='records')

    return render_template('homepage.html', movies=top_movies_data)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/movies-odds')
def index():
    """
    Displays the movie betting odds table
    """
    movie_stats_query = "SELECT * FROM movie_stats"
    movie_stats_df = pd.read_sql(movie_stats_query, db.engine)

    # query the db for the latest odds data
    goldderby_query = """
            SELECT "Movie Name", imp_prob_expert, imp_prob_user, imp_prob_star24, betting_pct, "Date"
            FROM goldderby
            WHERE "Date" = (SELECT MAX("Date") FROM goldderby)
        """
    goldderby_df = pd.read_sql(goldderby_query, db.engine)

    merged_df = pd.merge(movie_stats_df, goldderby_df, left_on="Movie Name", right_on="Movie Name", how="inner")

    # replacing movies that don't have odds with 'Unavailable' label
    def format_value(value):
        if pd.isna(value):
            return "Unavailable"
        return int(value)

    # Turning integer values into percentages
    def to_pct(value):
        if isinstance(value, int):
            return f"{value}%"
        return value


    # applying the above functions to clean the betting percentage and 'Difference' columns
    merged_df['betting_pct'] = merged_df['betting_pct'].apply(format_value)
    merged_df['Difference'] = merged_df['imp_prob_star24'].fillna(0) - merged_df['betting_pct'].replace("Unavailable",0)
    merged_df['Difference (Betting Odds vs. All Star)'] = merged_df.apply(
        lambda row: "Unavailable" if row['betting_pct'] == "Unavailable" or pd.isna(row['imp_prob_star24']) else row[
            'Difference'],axis=1)

    # movie name links to the movie's stats page
    merged_df['Movie Name'] = merged_df['Movie Name'].apply(lambda x: f'<a href="/movie/{x}">{x}</a>')

    # converting odds to percentages
    merged_df['Experts Odds'] = merged_df['imp_prob_expert'].apply(to_pct)
    merged_df['GoldDerby Users Odds'] = merged_df['imp_prob_user'].apply(to_pct)
    merged_df['All Star Users Odds'] = merged_df['imp_prob_star24'].apply(to_pct)
    merged_df['Betting Odds'] = merged_df['betting_pct'].apply(to_pct)

    latest_date = merged_df["Date"].iloc[0]

    merged_df = merged_df[["Movie Name", 'Experts Odds', 'GoldDerby Users Odds', 'All Star Users Odds', 'Betting Odds', 'Difference (Betting Odds vs. All Star)']]
    table_html = merged_df.to_html(classes='data', index=False, escape=False)

    return render_template('index.html', table=table_html, latest_date=latest_date)

@app.route('/win_votes_table')
def win_votes_table():
    """
    Displays the movie odds table that compares online betting odds to the percentage of voters who expect a movie to win
    """
    movie_stats_query = "SELECT * FROM movie_stats"
    movie_stats_df = pd.read_sql(movie_stats_query, db.engine)

    # instead of using goldderby's odds to compare to the betting odds, this table uses the % of voters who expect a movie to win as a proxy for the odds
    goldderby_query = """
            SELECT "Movie Name", pct_vote_expert, pct_vote_user, pct_vote_star24, betting_pct, "Date"
            FROM goldderby
            WHERE "Date" = (SELECT MAX("Date") FROM goldderby)
        """
    goldderby_df = pd.read_sql(goldderby_query, db.engine)

    merged_df = pd.merge(movie_stats_df, goldderby_df, left_on="Movie Name", right_on="Movie Name", how="inner")

    # replacing movies that don't have odds with 'Unavailable' label
    def format_value(value):
        if pd.isna(value):
            return "Unavailable"
        return int(value)

    # Turning integer values into percentages
    def to_pct(value):
        if isinstance(value, int):
            return f"{value}%"
        return value

    # applying the above functions to clean the betting percentage and 'Difference' columns
    merged_df['betting_pct'] = merged_df['betting_pct'].apply(format_value)
    merged_df['Difference'] = merged_df['pct_vote_star24'].fillna(0) - merged_df['betting_pct'].replace("Unavailable",0)
    merged_df['Difference (Betting Odds vs. All Star)'] = merged_df.apply(
        lambda row: "Unavailable" if row['betting_pct'] == "Unavailable" or pd.isna(row['pct_vote_star24']) else row[
            'Difference'],axis=1)

    # movie name links to the movie's stats page
    merged_df['Movie Name'] = merged_df['Movie Name'].apply(lambda x: f'<a href="/movie/{x}">{x}</a>')

    # converting odds to percentages
    merged_df['Experts Votes (%)'] = merged_df['pct_vote_expert'].apply(to_pct)
    merged_df['GoldDerby Users Votes (%)'] = merged_df['pct_vote_user'].apply(to_pct)
    merged_df['All Star Users Votes (%)'] = merged_df['pct_vote_star24'].apply(to_pct)
    merged_df['Betting Odds'] = merged_df['betting_pct'].apply(to_pct)

    latest_date = merged_df["Date"].iloc[0]

    merged_df = merged_df[["Movie Name", 'Experts Votes (%)', 'GoldDerby Users Votes (%)', 'All Star Users Votes (%)', 'Betting Odds', 'Difference (Betting Odds vs. All Star)']]
    table_html = merged_df.to_html(classes='data', index=False, escape=False)
    return render_template('win_votes.html', table=table_html, latest_date=latest_date)

@app.route('/movie/<movie_name>')
def movie_page(movie_name):
    """
    Extracts the stats and charts for a particular movie to be used in the individual movie pages
    """
    movie_stats_query = text("SELECT * FROM movie_stats WHERE \"Movie Name\" = :movie_name")
    movie_stats_df = pd.read_sql(movie_stats_query, db.engine, params={"movie_name": movie_name})

    if movie_stats_df.empty:
        return "Movie not found", 404

    probabilities_query = f"""
        SELECT "Date", "pct_vote_expert", "pct_vote_user", "pct_vote_star24", "betting_pct"
        FROM goldderby
        WHERE "Movie Name" = :movie_name
        ORDER BY "Date"
    """
    probabilities_df = pd.read_sql(probabilities_query, db.engine, params={"movie_name": movie_name})
    probabilities_json = probabilities_df.to_json(orient='records')

    # getting the latest news about the movie
    articles = get_news_for_movie(movie_name)

    return render_template('movie.html', movie_stats=movie_stats_df.iloc[0], chart_data=probabilities_json, articles = articles)



if __name__ == '__main__':
    app.run(debug=True if app.config['ENV'] == 'development' else False)