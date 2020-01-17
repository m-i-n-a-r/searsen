# Main file to build a trend based dataset. This script should run multiple times during the day, collecting the Google, Wikipedia and Twitter trends

import os
import sys
import csv
import pickle
from random import randint
import datetime
from pprint import pprint
from pathlib import Path
import pandas as pd
from sentistrength import PySentiStr
from pymongo import MongoClient
from extraction_google import fetch_trending_google
from extraction_twitter import fetch_trending_twitter
from extraction_twitter import fetch_sample
from extraction_wikipedia import fetch_trending_wikipedia
from keyword_matcher import get_all_matches
from searsen_credentials import mongo_username, mongo_password, sentistrength_jar_full_path, sentistrength_lan_full_path_en

# Add the current time and two lists of trends in a csv file
def update_trending_csv(google_trending, twitter_trending, wikipedia_trending, matching_trends, sentiment, sentiment_expanded):
    # Get the current time and create the file
    current_time = datetime.datetime.utcnow()
    trending_path = 'data/trending/'
    trending_file = trending_path + 'trending_google_twitter_wikipedia.csv'
    if not os.path.exists(trending_path): os.makedirs(trending_path)

    # Write the trending topics in a csv file
    f = Path(trending_file)
    if(not f.is_file()): 
        with open(trending_file, 'a', newline='', encoding='utf-8') as f:
            wr = csv.writer(f, delimiter=';')
            wr.writerow(['timpestamp', 'topics_google', 'topics_twitter', 'topics_wikipedia', 'matching_trends', 'sentiment', 'sentiment_expanded'])
    with open(trending_file, 'a', newline='', encoding='utf-8') as f:
        wr = csv.writer(f, delimiter=';')
        wr.writerow([current_time, google_trending, twitter_trending, wikipedia_trending, matching_trends, sentiment, sentiment_expanded])

# Add the current time and two lists of trends, plus a sample of tweets, in a mongodb table
def update_trending_mongo(google_trending, twitter_trending, wikipedia_trending, tweet_sample, matches, sentiment, sentiment_expanded, local = True):
    # Connect to MongoDB Atlas or to a local MongoDB installation
    if(local == False): client = MongoClient('mongodb+srv://' + mongo_username + ':' + mongo_password + '@searsen-fyfvz.mongodb.net/test?retryWrites=true&w=majority')
    else: client = MongoClient('mongodb://127.0.0.1:27017')

    db = client.searsendb_us
    # Create the object to store as a document. Every object is a row. Storing the tweets requires a lot of memory
    trend = {
        'date': datetime.datetime.utcnow(),
        'google': google_trending,
        'twitter': twitter_trending,
        'wikipedia': wikipedia_trending,
        'matches': matches,
        'sentiment': sentiment,
        'sentiment expanded': sentiment_expanded
        #'tweet_sample': tweet_sample
    }
    db.trends.insert_one(trend)

# Perform a sentiment analysis on a corpus of tweets, using sentistrength
def sentiment_analysis(tweet_sample, aggregate = True, mode = 'trinary'):
    senti = PySentiStr()
    senti.setSentiStrengthPath(sentistrength_jar_full_path)
    senti.setSentiStrengthLanguageFolderPath(sentistrength_lan_full_path_en)
    
    sentiment_dict = {}

    if type(tweet_sample) is not dict: return 'No matches'
    else:
        for topic in tweet_sample.keys():
            # Scores: scale, dual, binary and trinary
            sentiment = senti.getSentiment(tweet_sample[topic], score=mode)
            if (aggregate == True):
                sentisum = 0
                summary = {}
                for sent in sentiment: sentisum += sent[2] # The trinary score returns a tuple, unless the others
                summary['value'] = sentisum 
                if sentisum > 0: summary['sentiment'] = 'positive'
                else: summary['sentiment'] = 'negative'
                sentiment = summary
                
            sentiment_dict[topic] = sentiment
        return sentiment_dict
    

# Main part of searsen trending, it executes automatically
print('''
*************** SEARSEN ***************
Automatic trend and sentiment dataset builder
''')

# Some parameters and operations to manage the tweet sample extraction (the script should be executed every 20 or 30 minutes)
tweet_settings = 'tweet_sample_params'
wikipedia_trends_amount = 99
default_tweet_sample_skip = 0
tweet_sample_amount = 500

# Use Pickle to store and load the tweet_sample_skip variable
try:
    with open(tweet_settings, 'rb') as f:
        tweet_sample_skip = pickle.load(f)
except: 
    tweet_sample_skip = default_tweet_sample_skip   

# Fetch an ordered list of trends for Google, Twitter and Wikipedia and the matching trends list to collect a sample of tweets
google_trending = fetch_trending_google()
print('Fetched Google Trends')
twitter_trending = fetch_trending_twitter()
print('Fetched Twitter Trends')
wikipedia_trending = fetch_trending_wikipedia(wikipedia_trends_amount)
print('Fetched Wikipedia Trends')

# Get a dictionary containing the matches of each combination of the three sources
matches = get_all_matches(google_trending, twitter_trending, wikipedia_trending)
print('Matches computed')

# Check if the tweet sample should be skipped in the current execution
if(tweet_sample_skip == 0): 
    tweet_sample = fetch_sample(matches['twitter-google'], tweet_sample_amount)
    print('Fetched tweet sample')
    # Live sentiment analysis on the google-twitter matches (trinary aggregated, scale not aggregated)
    sentiment = sentiment_analysis(tweet_sample)
    sentiment_expanded = sentiment_analysis(tweet_sample, False, 'scale')
    print('Sentiment computed')
    with open(tweet_settings, 'wb') as f:
        pickle.dump(default_tweet_sample_skip, f)
else: 
    tweet_sample = 'Skipped'
    sentiment = 'Skipped'
    sentiment_expanded = 'Skipped'
    with open(tweet_settings, 'wb') as f:
        pickle.dump(tweet_sample_skip-1, f)

# Insert the data in a csv file or in MongoDB (Atlas or local, default is local)
#update_trending_csv(google_trending, twitter_trending, wikipedia_trending, matches, sentiment, sentiment_expanded)
update_trending_mongo(google_trending, twitter_trending, wikipedia_trending, tweet_sample, matches, sentiment, sentiment_expanded)
print('Data saved')

print('\n***************** Done *****************\n')