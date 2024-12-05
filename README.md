# best-picture-odds
Python-based app that compares Oscars Best Picture betting odds from popular betting sites with expert predictions, highlighting significant discrepancies and aggregating stats and news related to each contending movie

Overview:
<br>
I love movies and every year, I compete with my friends to see which one of us can get the most predictions correct for the Oscar winners. Though I don’t do any sort of real betting, I thought it would be interesting to build an app that compares the betting odds for the Best Picture category at the Oscars from popular betting sites (using betting APIs like Betfair, Pinnacle, or OddsAPI) to expert predictions from the GoldDerby website (which is where anyone can enter their predictions for the Oscars. The app highlights discrepancies between these two sources. For example, if experts give a film a high chance of winning (50%) but the betting odds suggest it’s a long shot (10%), the app highlights these differences. 
<br>
In addition, for each Best Picture nominee, the app:
<br>
Fetches movie stats (e.g., ratings, director, cast) from the OMDb or IMDb API
<br>
Pulls the latest news article about the movie using the NewsAPI to give users more context around the awards buzz.
<br>
<br>
Tools I used:
Betting API: Oddschecker for betting odds.
<br>
GoldDerby Predictions: Data scraping from GoldDerby for expert predictions
<br>
OMDb/IMDb API: For movie stats
<br>
NewsAPI: To find and display news articles related to each movie
<br><br>

Execution Plan:
<br>
Week 4:
<br>
Research and integrate the betting API for real-time odds
<br>
Set up a method to gather GoldDerby predictions (either through web scraping or any available API)
<br>
Week 5:
<br>
Buffer week to ensure accurate odds and prediction data is being retrieved
<br>
Week 6:
<br>
Implement comparison logic to highlight discrepancies between betting odds and expert predictions
<br>
Add OMDb/IMDb API integration to fetch movie details for each nominee
<br>
Week 7:
<br>
Integrate NewsAPI to display the latest news articles about each movie.
<br>
Week 8:
<br>
Finalize the project by refining the UI/UX, testing data retrieval, and deploying the app
<br>
<br>
To replicate:
<br>
1. Clone the repo
2. Navigate to the odds-app folder
3. Set up a virtual environment and install dependencies: pip install -r requirements.txt
4. Create a .env file and copy the variables from the .env.example file into it
5. Set up the database by running create_db.py. If the local.db file is created within a directory called 'instance', you may need to copy the local.db file into the odds-app folder for the app to function properly.
6. Run the flask app

