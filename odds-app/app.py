from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

app = Flask(__name__)
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')

uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgresql://"):
    uri = uri.replace("postgresql://", 'postgresql+psycopg://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

omdb_api_key = os.environ.get('OMDB_API_KEY')

@app.route('/')
def index():
    movie_stats_query = "SELECT * FROM movie_stats"
    movie_stats_df = pd.read_sql(movie_stats_query, db.engine)

    goldderby_query = """
            SELECT "Movie Name", imp_prob_expert, imp_prob_user, imp_prob_star24, betting_pct, "Date"
            FROM goldderby
            WHERE "Date" = (SELECT MAX("Date") FROM goldderby)
        """
    goldderby_df = pd.read_sql(goldderby_query, db.engine)

    merged_df = pd.merge(movie_stats_df, goldderby_df, left_on="Movie Name", right_on="Movie Name", how="inner")

    def format_value(value):
        if pd.isna(value):
            return "Unavailable"
        return int(value)

    def to_pct(value):
        if isinstance(value, int):
            return f"{value}%"
        return value


    merged_df['betting_pct'] = merged_df['betting_pct'].apply(format_value)
    merged_df['Difference'] = merged_df['imp_prob_star24'].fillna(0) - merged_df['betting_pct'].replace("Unavailable",0)
    merged_df['Difference'] = merged_df.apply(
        lambda row: "Unavailable" if row['betting_pct'] == "Unavailable" or pd.isna(row['imp_prob_star24']) else row[
            'Difference'],axis=1)

    merged_df['Movie Name'] = merged_df['Movie Name'].apply(lambda x: f'<a href="/movie/{x}">{x}</a>')
    merged_df['imp_prob_expert'] = merged_df['imp_prob_expert'].apply(to_pct)
    merged_df['imp_prob_user'] = merged_df['imp_prob_user'].apply(to_pct)
    merged_df['imp_prob_star24'] = merged_df['imp_prob_star24'].apply(to_pct)
    merged_df['betting_pct'] = merged_df['betting_pct'].apply(to_pct)
    merged_df = merged_df[["Movie Name", 'imp_prob_expert', 'imp_prob_user', 'imp_prob_star24', 'betting_pct', "Date", 'Difference']]
    table_html = merged_df.to_html(classes='data', index=False, escape=False)
    return render_template('index.html', table=table_html)

@app.route('/movie/<movie_name>')
def movie_page(movie_name):
    movie_stats_query = f'SELECT * FROM movie_stats WHERE "Movie Name" = %s'
    movie_stats_df = pd.read_sql(movie_stats_query, db.engine, params=[(movie_name,)])

    if movie_stats_df.empty:
        return "Movie not found", 404

    probabilities_query = f"""
        SELECT "Date", "imp_prob_expert", "imp_prob_user", "imp_prob_star24", "betting_pct"
        FROM goldderby
        WHERE "Movie Name" = %s
        ORDER BY "Date"
    """
    probabilities_df = pd.read_sql(probabilities_query, db.engine, params=[(movie_name,)])
    probabilities_json = probabilities_df.to_json(orient='records')

    return render_template('movie.html', movie_stats=movie_stats_df.iloc[0], chart_data=probabilities_json)



if __name__ == '__main__':
    app.run(debug=True if app.config['ENV'] == 'development' else False)