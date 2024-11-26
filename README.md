# best-picture-odds
Python-based app that compares Oscars Best Picture betting odds from popular betting sites with expert predictions, highlighting significant discrepancies and aggregating stats and news related to each contending movie

Overview:
<br>
I love movies and every year, I compete with my friends to see which one of us can get the most predictions correct for the Oscar winners. Though I don’t do any sort of real betting, I thought it would be interesting to build an app that compares the betting odds for the Best Picture category at the Oscars from popular betting sites (using betting APIs like Betfair, Pinnacle, or OddsAPI) to expert predictions from the GoldDerby website (which is where anyone can enter their predictions for the Oscars. The app will highlight discrepancies between these two sources. For example, if experts give a film a high chance of winning (50%) but the betting odds suggest it’s a long shot (10%), the app will highlight these differences. 
<br>
In addition, for each Best Picture nominee, the app will:
<br>
Fetch movie stats (e.g., ratings, director, cast) from the OMDb or IMDb API
<br>
Pull the latest news article about the movie using the NewsAPI to give users more context around the awards buzz.
<br>
<br>
Tools I’ll use:
Betting API: Use Betfair, Pinnacle, or OddsAPI for betting odds.
<br>
GoldDerby Predictions: Data scraping from GoldDerby for expert predictions
<br>
OMDb/IMDb API: for movie stats
<br>
NewsAPI: to find and display news articles related to each movie
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
Note about replicating: Replicating this app would require access to API keys for OMDB and News API. The app also queries the two SQL database tables, 'goldderby' and 'movie_stats' table, which I have uploaded in the SQL_table_files folder in the repo. Replicating this would still require a specific setup of postgres and converting those csv files to SQL tables on the machine you want to run the app on.
