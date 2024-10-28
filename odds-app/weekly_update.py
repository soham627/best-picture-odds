import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from bs4 import BeautifulSoup

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL').replace('postgresql://', 'postgresql+psycopg://'))

def odds_clean(odds):
    if odds[-1] == "-":
        return odds[:-1]
    else:
        return odds

def calculate_pct_votes(df, vote_column, date_column='Date'):
    total_votes_per_date = df.groupby(date_column)[vote_column].transform('sum')
    pct_votes = (df[vote_column] / total_votes_per_date * 100).round().astype(int)
    return pct_votes


def odds_to_prob(odds):
    try:
        if '/' in odds:
            vals = odds.split('/')
            numerator, denominator = int(vals[0]), int(vals[1])
            prob = (denominator / (numerator + denominator)) * 100
        else:
            decimal_odds = float(odds)
            prob = (1 / decimal_odds) * 100

        rounded_prob = int(round(prob))
        return rounded_prob
    except:
        return None


def find_movies(url, movies_df):
    movie_names = set(movies_df['Movie Name'].tolist())
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    odds_page = soup.find('div', id='odds-page')
    if not odds_page:
        return None

    best_picture_section = None
    for title in odds_page.find_all('div', class_='category-title'):
        if 'Best Picture' in title.get_text(strip=True):
            best_picture_section = title
            break

    if not best_picture_section:
        return None

    predictions_list = best_picture_section.find_next('ul', class_='predictions-list')
    if not predictions_list:
        return None

    movies_and_predictions = []
    for item in predictions_list.find_all('li'):
        movie_name = item.find('div', class_='predictions-name').get_text(strip=True)
        if movie_name in movie_names:
            odds_elements = item.find_all('div', class_='predictions-odds')
            if len(odds_elements) >= 3:
                nomination = odds_elements[0].get_text(strip=True)
                try:
                    win = int(odds_elements[1].get_text(strip=True))
                except ValueError:
                    win = 0
                odds = odds_elements[2].get_text(strip=True)
                movies_and_predictions.append({
                    'Movie Name': movie_name,
                    'Nomination Vote': nomination,
                    'Win Vote': win,
                    'Odds': odds_clean(odds)
                })
    return movies_and_predictions

# URLs for each category
base_urls = {
    'Experts': "https://www.goldderby.com/odds/expert-odds/oscars-nominations-2025-predictions/",
    'Star24': "https://www.goldderby.com/odds/star24-odds/oscars-nominations-2025-predictions/",
    'Users': "https://www.goldderby.com/odds/user-odds/oscars-nominations-2025-predictions/"
}

# Load movies list
movies_df = pd.read_csv('movies_df.csv')

# Scrape data
all_data = []
data_experts = find_movies(base_urls['Experts'], movies_df) or []
data_star24 = find_movies(base_urls['Star24'], movies_df) or []
data_users = find_movies(base_urls['Users'], movies_df) or []

# Process combined data
combined_data = {}
for movie in data_experts:
    combined_data[movie['Movie Name']] = {
        'Movie Name': movie['Movie Name'],
        'Experts Vote': movie['Win Vote'],
        'Experts Odds': movie['Odds'],
        'Star24 Vote': 'N/A',
        'Star24 Odds': 'N/A',
        'Users Vote': 'N/A',
        'Users Odds': 'N/A',
        'Date': datetime.now().strftime('%Y-%m-%d')
    }

for movie in data_star24:
    if movie['Movie Name'] in combined_data:
        combined_data[movie['Movie Name']]['Star24 Vote'] = int(movie['Win Vote'])
        combined_data[movie['Movie Name']]['Star24 Odds'] = movie['Odds']
    else:
        combined_data[movie['Movie Name']] = {
            'Movie Name': movie['Movie Name'],
            'Experts Vote': 'N/A',
            'Experts Odds': 'N/A',
            'Star24 Vote': movie['Win Vote'],
            'Star24 Odds': movie['Odds'],
            'Users Vote': 'N/A',
            'Users Odds': 'N/A',
            'Date': datetime.now().strftime('%Y-%m-%d')
        }

for movie in data_users:
    if movie['Movie Name'] in combined_data:
        combined_data[movie['Movie Name']]['Users Vote'] = int(movie['Win Vote'])
        combined_data[movie['Movie Name']]['Users Odds'] = movie['Odds']
    else:
        combined_data[movie['Movie Name']] = {
            'Movie Name': movie['Movie Name'],
            'Experts Vote': 'N/A',
            'Experts Odds': 'N/A',
            'Star24 Vote': 'N/A',
            'Star24 Odds': 'N/A',
            'Users Vote': movie['Win Vote'],
            'Users Odds': movie['Odds'],
            'Date': datetime.now().strftime('%Y-%m-%d')
        }

all_data.extend(combined_data.values())

# Create df and calculate percentages and implied probabilities
weekly_df = pd.DataFrame(all_data)
weekly_df['pct_vote_expert'] = calculate_pct_votes(weekly_df, 'Experts Vote')
weekly_df['pct_vote_star24'] = calculate_pct_votes(weekly_df, 'Star24 Vote')
weekly_df['pct_vote_user'] = calculate_pct_votes(weekly_df, 'Users Vote')

weekly_df['imp_prob_expert'] = weekly_df['Experts Odds'].apply(lambda x: odds_to_prob(x) if x != 'N/A' else None)
weekly_df['imp_prob_star24'] = weekly_df['Star24 Odds'].apply(lambda x: odds_to_prob(x) if x != 'N/A' else None)
weekly_df['imp_prob_user'] = weekly_df['Users Odds'].apply(lambda x: odds_to_prob(x) if x != 'N/A' else None)

movie_names = set(movies_df['Movie Name'].tolist())

## getting the betting site odds data
api_response = requests.post(
    "https://api.zyte.com/v1/extract",
    auth=(os.getenv("ZYTE_API_KEY"), ""),
    json={
        "url": "https://www.oddschecker.com/awards/oscars/best-picture",
        "browserHtml": True,
    },
)
browser_html = api_response.json()["browserHtml"]
soup = BeautifulSoup(browser_html, 'html.parser')

title_mapping = {
    'Joker: Folie à Deux': 'Joker: Folie a Deux',
    'Gladiator II': 'Gladiator 2',
    'Nickel Boys': 'The Nickel Boys',
    'Saturday Night': 'SNL: 1975'
}

def find_odds_for_movie(movie_name, soup):
    betting_title = title_mapping.get(movie_name, movie_name)
    movie_tag = soup.find('span', {'data-name': betting_title})


    if not movie_tag:
        print(f"Warning: Movie '{movie_name}' with betting title '{betting_title}' not found in HTML.")
        return None

    ew_tag = movie_tag.find_next(
        lambda tag: tag.name == 'td' and tag.has_attr('data-best-ew') and tag['data-best-ew'] == 'true')

    if not ew_tag:
        print(f"Warning: data-best-ew='true' not found for movie '{movie_name}'.")
        return None


    odds_value = ew_tag.get('data-o', None)

    if not odds_value:
        p_tag = ew_tag.find('p')
        odds_value = p_tag.get_text(strip=True) if p_tag else None

    return odds_value

weekly_df['betting_odds'] = weekly_df['Movie Name'].apply(lambda name: find_odds_for_movie(name, soup))
weekly_df['betting_pct'] = weekly_df['betting_odds'].apply(lambda x: odds_to_prob(x) if x != 'N/A' else None)


# Save to database
weekly_df.to_sql('goldderby', engine, if_exists='append', index=False)

