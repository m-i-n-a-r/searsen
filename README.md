# Searsen - search vs sentiment
<p align="center>
	<img src="https://img.shields.io/badge/status-work%20in%20progress-orange" width="20%" />
	<img src="https://img.shields.io/badge/version-0.2-blue" width="20%" />
</p>

### An attempt to use Google Trends and Twitter to find the relation between searches and opinions

## Introduction and desired goal
Google, togheter with the social networks, is a useful source of informations on how a theme is perceived in a specific geographic area.
While Google Trends offers monthly or daily data, Twitter has a set of powerful API to get the trending topics and search for specific keywords. Google Trends data are normalized in a 0-100 range.
The desired goal is to perform an analysis, comparing a dataset from Google Trends with the data from Twitter or other social networks, trying to find the relations and using them in a machine learning system (prediction, recomendation), if possible. In addition, Searsen is able to build a dataset fetching the hot trends from Google and the trending topics from Twitter: this dataset is used to understand the similarities and correlations between this two kind of trends.

## Project structure
At the time of writing, the project consistis in 4 main files:
- extraction_twitter :arrow_forward: extracts data from Twitter. It can extract both time series or trending topics
- extraction_google :arrow_forward: extracts data from Google. It can extract both time series or hot trends
- searsen_timeseries :arrow_forward: analyzes and plot the timeseries on user input. Useful to compare the overall trends of a keyword
- searsen_trends :arrow_forward: aggregates the current time, the trending topics and the hot trends in a single csv file

