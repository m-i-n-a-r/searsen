# Main file for trending keywords. This script should run multiple times during the day, collecting Twitter the trending topics and the Google hot trends

import os
import sys
import csv
from random import randint
import datetime
from pprint import pprint
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from pymongo import MongoClient
from extraction_google import fetch_trending_google
from extraction_twitter import fetch_trending_twitter
from extraction_twitter import fetch_sample
from extraction_wikipedia import fetch_trending_wikipedia
from searsen_credentials import mongo_username, mongo_password

# Add the current time and two lists of trends in a csv file
def update_trending_csv(google_trending, twitter_trending, wikipedia_trending, matching_trends):
    # Get the current time and create the file
    current_time = datetime.datetime.utcnow()
    trending_path = 'data/trending/'
    trending_file = trending_path + 'trending_google_twitter.csv'
    if not os.path.exists(trending_path): os.makedirs(trending_path)

    # Write the trending topics in a csv file
    f = Path(trending_file)
    if(not f.is_file()): 
        with open(trending_file, 'a', newline='') as f:
            wr = csv.writer(f, delimiter=';')
            wr.writerow(['timpestamp', 'topics_google', 'topics_twitter', 'topics_wikipedia', 'matching_trends'])
    with open(trending_file, 'a', newline='') as f:
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
    print('Finished\n')

# Compare two lists of trends (Twitter and Google) and return a list of keywords
def compare_trends(google_trending, twitter_trending):
    # Pre-elaboration and intersection
    processed_google = [trend.lower().replace(' ', '') for trend in google_trending]
    processed_twitter = [trend.lower().replace(' ', '') for trend in twitter_trending]
    matching_trends = list(set(processed_google) & set(processed_twitter))

    return matching_trends

# Compare three lists of trends (Twitter, Google and Wikipedia) and return a list of keywords
def compare_trends_all(google_trending, twitter_trending, wikipedia_trending):
    processed_google = [trend.lower().replace(' ', '') for trend in google_trending]
    processed_twitter = [trend.lower().replace(' ', '') for trend in twitter_trending]
    processed_wikipedia = [trend.lower().replace('_', '') for trend in wikipedia_trending]
    matching_trends_all = list(set(processed_google) & set(processed_twitter) & set(processed_wikipedia))

    return matching_trends_all

# Main part of searsen trending, it executes automatically
print('''
*************** SEARSEN ***************
Extract and compare searches and sentiment
''')

# Fetch an ordered list of trends for Google, Twitter and Wikipedia and the matching trends list to collect a sample of tweets
google_trending = fetch_trending_google()
twitter_trending = fetch_trending_twitter()
wikipedia_trending = fetch_trending_wikipedia()
matching_trends = compare_trends(google_trending, twitter_trending)
matching_trends_all = compare_trends_all(google_trending, twitter_trending, wikipedia_trending)
tweet_sample = fetch_sample(matching_trends)

# Insert the data in a csv file and in MongoDB
update_trending_csv(google_trending, twitter_trending, wikipedia_trending, matching_trends)
update_trending_mongo(google_trending, twitter_trending, wikipedia_trending, tweet_sample)