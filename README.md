# Searsen - SEarch, ARticle, SENtiment
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

The language used is english(US), and previously italian.

## Project structure
At the time of writing, the project consistis in 5 main files (3 for data extraction, 2 for data analysis):
- **extraction_twitter** :arrow_forward: extracts data from Twitter. It can extract both time series, trending topics or tweets for a given keyword
- **extraction_google** :arrow_forward: extracts data from Google. It can extract both time series or hot trends
- **extraction_wikipedia** :arrow_forward: extracts data from Wikipedia. It can extract both time series or trending articles
- **keyword_matcher** :arrow_forward: contains a number of matching criteria, to detect the eventual relation between two different keywords or to match similar or identical keywords [WIP]
- **searsen_timeseries** :arrow_forward: analyzes and plot the timeseries on user input. Useful to compare the overall trends of a keyword [WIP]
- **searsen_trends** :arrow_forward: aggregates the current time, the Twitter trending topics, the Google hot trends and the Wikipedia top articles in a single csv file or in a MongoDB table, thus generating a dataset. It also gets a list of tweets for each topic contained both in hot trends and trending topics and calculates the sentiment
- **searsen_automate** :arrow_forward: a batch file to execute the dataset generator.It can be used to automate the execution of the script on a Windows machine, using the [Windows Task Scheduler](https://datatofish.com/python-script-windows-scheduler/). Remember to set the right full path to the searsen_trending script in your machine.

## How to
Searsen requires some libraries (listed below) to work, plus some extra informations. Create a file called **searsen_credentials.py**, and make sure it contains:
- The credentials of your Twitter application. To create one, simply [create a developer account](https://docs.inboundnow.com/guide/create-twitter-application/) on Twitter.
- The credentials of your [MongoDB Atlas](https://www.mongodb.com/cloud/atlas), if it's being used.
- The full path to the language folder for [Sentistrength](http://sentistrength.wlv.ac.uk/), and the full path for the Sentistrength .jar file. Sentistrength and the language packs are not included, but you can easily find the language packs online, and request the jar by contacting the owner.

## Libraries and external requirements
Searsen uses some third party software to work properly. Some examples are:
- **Pytrends**
- **Tweepy** (including the credentials of a Twitter application)
- **Pageview API**
- **Sentistrength** (Python API + java version and language packs)
- **Pandas**
- **Pickle**
- **Pymongo** (MongoDB Atlas or local)
- **Difflib**