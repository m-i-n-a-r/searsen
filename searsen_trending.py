# Main file for trending keywords. This script should run multiple times during the day, collecting Twitter the trending topics and the Google hot trends

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
from keyword_matcher import advanced_matching
from searsen_credentials import mongo_username, mongo_password

# Add the current time and two lists of trends in a csv file
def update_trending_csv(google_trending, twitter_trending, wikipedia_trending, matching_trends):
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
            wr.writerow(['timpestamp', 'topics_google', 'topics_twitter', 'topics_wikipedia', 'matching_trends'])
    with open(trending_file, 'a', newline='', encoding='utf-8') as f:
        wr = csv.writer(f, delimiter=';')
        wr.writerow([current_time, google_trending, twitter_trending, wikipedia_trending, matching_trends])

# Add the current time and two lists of trends, plus a sample of tweets, in a mongodb table
def update_trending_mongo(google_trending, twitter_trending, wikipedia_trending, tweet_sample):
    # Connect to MongoDB
    client = MongoClient('mongodb+srv://' + mongo_username + ':' + mongo_password + '@searsen-fyfvz.mongodb.net/test?retryWrites=true&w=majority')
    db = client.searsen
    # Create the object to store as a document. Every object is a row
    trend = {
        'date': datetime.datetime.utcnow(),
        'google': google_trending,
        'twitter': twitter_trending,
        'wikipedia': wikipedia_trending,
        'tweet_sample': tweet_sample
    }
    db.trends.insert_one(trend)

# Perform a sentiment analysis on a corpus of tweets, using sentistrength
def sentiment_analysis(tweet_sample):
    senti = PySentiStr()
    senti.setSentiStrengthPath('/sentistrength/SentiStrengthCom.jar')
    senti.setSentiStrengthLanguageFolderPath('/sentistrength/italian/')
    sentiment_dict = []
    if type(tweet_sample) is not dict: return 'Error'
    else:
        for topic in tweet_sample.keys():
            sentiment = senti.getSentiment(tweet_sample[topic], score='binary')
            print(sentiment) # TODO remove
            sentiment_dict[topic] = sentiment
        return sentiment_dict
    

# Main part of searsen trending, it executes automatically
print('''
*************** SEARSEN ***************
Extract and compare searches and sentiment
''')

# Some parameters and operations to manage the tweet sample extraction (the script should be executed every 20 or 30 minutes)
tweet_settings = 'tweet_sample_params'
wikipedia_trends_amount = 50
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
twitter_trending = fetch_trending_twitter()
wikipedia_trending = fetch_trending_wikipedia(wikipedia_trends_amount)
matching_trends_advanced = advanced_matching(google_trending, twitter_trending)

# Check if the tweet sample should be skipped in the current execution
if(tweet_sample_skip == 0): 
    tweet_sample = fetch_sample(matching_trends_advanced, tweet_sample_amount)
    # Live sentiment analysis
    #sentiment = sentiment_analysis(tweet_sample)
    with open(tweet_settings, 'wb') as f:
        pickle.dump(default_tweet_sample_skip, f)
else: 
    tweet_sample = 'Skipped'
    with open(tweet_settings, 'wb') as f:
        pickle.dump(tweet_sample_skip-1, f)

# Insert the data in a csv file or in MongoDB
#update_trending_csv(google_trending, twitter_trending, wikipedia_trending, matching_trends_advanced)
update_trending_mongo(google_trending, twitter_trending, wikipedia_trending, tweet_sample)

print('******** Done ********\n')