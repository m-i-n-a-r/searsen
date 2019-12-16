# Searsen - search vs sentiment
### An attempt to use Google Trends, Twitter and Wikipedia to find the relation between interest, search and opinion

<p align=center>
	<img src='https://img.shields.io/badge/version-0.3-blue'/>
	<img src='https://img.shields.io/badge/status-wip-orange'/>
	<img src='https://img.shields.io/badge/python-3.6+-success'/>
	<img src='https://img.shields.io/badge/-master%20thesis-yellow'/>
</p>

## Introduction and desired goal
Google, togheter with the social networks, is a useful source of informations on how a theme is perceived in a specific geographic area.
While Google Trends offers monthly or daily data, Twitter has a set of powerful API to get the trending topics and search for specific keywords. Google Trends data are normalized in a 0-100 range.
The desired goal is to perform an analysis, comparing a dataset from Google Trends with the data from Twitter or other social networks, trying to find the relations and using them in a machine learning system (prediction, recomendation), if possible. In addition, Searsen is able to build a dataset fetching the hot trends from Google and the trending topics from Twitter: this dataset is used to understand the similarities and correlations between this two kind of trends.

## Project structure
At the time of writing, the project consistis in 5 main files (3 for data extraction, 2 for data analysis):
- **extraction_twitter** :arrow_forward: extracts data from Twitter. It can extract both time series, trending topics or tweets for a given keyword
- **extraction_google** :arrow_forward: extracts data from Google. It can extract both time series or hot trends
- **extraction_wikipedia** :arrow_forward: extracts data from Wikipedia. It can extract both time series or trending articles
- **searsen_timeseries** :arrow_forward: analyzes and plot the timeseries on user input. Useful to compare the overall trends of a keyword [WIP]
- **searsen_trends** :arrow_forward: aggregates the current time, the Twitter trending topics, the Google hot trends and the Wikipedia top articles in a single csv file or in a MongoDB table, getting a list of tweets for each topic contained both in hot trends and trending topics

## Libraries and external requirements
This software uses some third party software to work properly. Some examples are
- **Pytrends**
- **Tweepy**
- **Pageview API**
- **Sentistrength** (Python API + java version and language packs)
- **Pandas**
- **Pickle**
- **Pymongo**
