# Twitter data extraction - use Tweepy to extract the data about a group of hashtags

import tweepy
import csv
from twitter_app_credentials import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Variabled needed (tries to take it from user or use default)
separator = ','
input_keyword = input('Insert a keyword (default: trump)')
if(not input_keyword.strip()): keyword = 'trump'
else: keyword = input_keyword

def fetch_csv_twitter(keyword):
    # Csv name
    data_path = 'data/twitter/'
    file_name = data_path + keyword.replace(' ', '') + '_twitter_interest.csv'

    # Open/create a file to append data to
    csv_file = open(file_name, 'a')
    #Use csv writer
    csv_writer = csv.writer(csv_file)
    tweets = tweepy.Cursor(api.search, q=keyword, since="2019-02-14", until="2019-02-15", lang="en")
    print(tweets)

    for tweet in tweets.items():
        # Write a row to the CSV file. I use encode UTF-8
        csv_writer.writerow([tweet.created_at, tweet.text.encode('utf-8')])
        print(tweet.created_at, tweet.text)
    csv_file.close()

fetch_csv_twitter(keyword)