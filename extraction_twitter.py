# Twitter data extraction - use Tweepy to extract the data about a group of hashtags

import tweepy
import csv
import pandas as pd
from twitter_app_credentials import *

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

def fetch_csv_twitter(keyword):
    # Csv name
    data_path = 'data/twitter/'
    file_name = data_path + keyword.replace(' ', '') + '_twitter_interest.csv'
    tweets = []

    # append all tweet data to list
    items = tweepy.Cursor(api.search, q=keyword, count=10, since="2019-11-03").items()
    print(items)
    for tweet in items:
        tweets.append(tweet)

    # convert 'tweets' list to pandas.DataFrame
    tweets_df = pd.DataFrame(vars(tweets[i]) for i in range(len(tweets)))

    # use pandas to save dataframe to csv
    tweets_df.to_csv(file_name)

# Avoid to run the script when imported
if __name__ == '__main__':
    # Variabled needed (tries to take it from user or use default)
    separator = ','
    input_keyword = input('Insert a keyword (default: trump) -> ')
    if(not input_keyword.strip()): keyword = 'trump'
    else: keyword = input_keyword

    fetch_csv_twitter(keyword)