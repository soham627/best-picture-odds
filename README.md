# best-picture-odds
Python-based app that compares Oscars Best Picture betting odds from popular betting sites with expert predictions, highlighting significant discrepancies and aggregating stats and news related to each contending movie

Overview:
I love movies and every year, I compete with my friends to see which one of us can get the most predictions correct for the Oscar winners. Though I don’t do any sort of real betting, I thought it would be interesting to build an app that compares the betting odds for the Best Picture category at the Oscars from popular betting sites (using betting APIs like Betfair, Pinnacle, or OddsAPI) to expert predictions from the GoldDerby website (which is where anyone can enter their predictions for the Oscars. The app will highlight discrepancies between these two sources. For example, if experts give a film a high chance of winning (50%) but the betting odds suggest it’s a long shot (10%), the app will highlight these differences. 
In addition, for each Best Picture nominee, the app will:
Fetch movie stats (e.g., ratings, director, cast) from the OMDb or IMDb API
Pull the latest news article about the movie using the NewsAPI to give users more context around the awards buzz.
Tools I’ll use:
Betting API: Use Betfair, Pinnacle, or OddsAPI for betting odds.
GoldDerby Predictions: Data scraping from GoldDerby for expert predictions
OMDb/IMDb API: for movie stats
NewsAPI: to find and display news articles related to each movie

Execution Plan:
Week 4:
Research and integrate the betting API for real-time odds
Set up a method to gather GoldDerby predictions (either through web scraping or any available API)
Week 5:
Buffer week to ensure accurate odds and prediction data is being retrieved
Week 6:
Implement comparison logic to highlight discrepancies between betting odds and expert predictions
Add OMDb/IMDb API integration to fetch movie details for each nominee
Week 7:
Integrate NewsAPI to display the latest news articles about each movie.
Week 8:
Finalize the project by refining the UI/UX, testing data retrieval, and deploying the app

