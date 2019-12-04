# Twitter data extraction - using Tweepy

import os
import tweepy
import csv
import pandas as pd
from searsen_credentials import consumer_key, consumer_secret, access_token, access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Fetch the use of a particular keyword over time
def fetch_timeseries_twitter(keyword, save_csv = True):
    tweets = []

    # Append all tweet data to list
    tweet_items = tweepy.Cursor(api.search, q=keyword, result_type='mixed').items(100)
    for tweet in tweet_items: tweets.append(tweet)

    # Convert 'tweets' list to pandas.DataFrame
    tweets_df = pd.DataFrame(vars(tweets[i]) for i in range(len(tweets)))

    # Save in a csv if needed
    if(save_csv): 
        # Csv naming and path, converting to csv using Pandas
        data_path = 'data/twitter/'
        if not os.path.exists(data_path): os.makedirs(data_path)
        file_name = data_path + keyword.replace(' ', '') + '_twitter_interest.csv'
        tweets_df.to_csv(file_name, sep=';')
    
    return tweets_df

# Get trending topics in Italy as an ordered list (US code = 2352824)
def fetch_trending_twitter():   
    trends_it = api.trends_place('711080')
    data = trends_it[0] 
    # Take the name of the trends
    trends_name = data['trends']
    trends_it_final = [trend['name'].replace('#', '') for trend in trends_name]
    
    return trends_it_final

# Fetch a sample of n tweets for every keyword in a given list
def fetch_sample(keywords):
    tweets = []
    # Fill a list with the tweets
    for keyword in keywords:
        tweet_items = tweepy.Cursor(api.search, q=keyword, result_type='mixed').items(1000)
        for tweet in tweet_items: tweets.append(tweet)
    
    return keywords


# Avoid to run the script when imported
if __name__ == '__main__':
    # Variabled needed (tries to take it from user or use default)
    input_keyword = input('\nInsert a keyword (default: trump) -> ')
    if(not input_keyword.strip()): keyword = 'trump'
    else: keyword = input_keyword

    fetch_timeseries_twitter(keyword)