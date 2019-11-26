# Main file for trending keywords. This script should run multiple times during the day, collecting Twitter the trending topics and the Google hot trends

import os
import sys
import csv
import datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from extraction_google import fetch_trending_google
from extraction_twitter import fetch_trending_twitter

trending_path = 'data/trending/'
trending_file = trending_path + 'trending_google_twitter.csv'
if not os.path.exists(trending_path): os.makedirs(trending_path)

print('''
*************** SEARSEN ***************
Extract and compare searches and sentiment

Fetching the latest trends from Google and Twitter...
''')

current_time = datetime.datetime.now()
google_trending = fetch_trending_google()
twitter_trending = fetch_trending_twitter()

print('\n########### GOOGLE ###########\n')
print(google_trending)
print('\n########### TWITTER ###########\n')
print(twitter_trending)
print('\n')

# Write the trending topics in a csv file
f = Path(trending_file)
if(not f.is_file()): 
    with open(trending_file, 'a', newline='') as f:
        wr = csv.writer(f, delimiter=';')
        wr.writerow(['timpestamp', 'topics_google', 'topics_twitter'])

with open(trending_file, 'a', newline='') as f:
    wr = csv.writer(f, delimiter=';')
    wr.writerow([current_time, google_trending, twitter_trending])
