# Provide some useful functions to analyze the dataset

from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# Given a keyword, check how many hours it was in the trends
def trend_lifecycle(trend):
    return

# Compare two set of trends shifting them in time (eg Twitter trends at 7 AM vs Google trends at 9 AM)
def trend_shifted_comparison():
    return

# Estimate the polarization for a selected keyword
def estimate_polarization():
    return

# Iterate over all the documents and count
def catalog_trends(trends, source):
    match_counter = {}
    for document in trends:
        matches = []   
        if(source == 'google'): matches = document['google']
        elif(source == 'twitter'): matches = document['twitter']
        elif(source == 'wikipedia'): matches = document['wikipedia']
        elif(source == 'twitter-google'): matches = document['matches']['twitter-google']
        elif(source == 'twitter-wikipedia'): matches = document['matches']['twitter-wikipedia']
        elif(source == 'google-wikipedia'): matches = document['matches']['google-wikipedia']
        elif(source == 'google-twitter-wikipedia'): matches = document['matches']['google-twitter-wikipedia']
        else: matches = document['google']

        if(isinstance(matches, list) and matches):
            for trend in matches:
                if trend in match_counter: match_counter[trend] += 1
                else: match_counter[trend] = 1

    # Sort by descending value
    match_counter = {k: v for k, v in sorted(match_counter.items(), key=lambda item: item[1], reverse=True)}
    return match_counter

# Accept a catalogued trend list, take the first n trends and let the user assign them to a class
def manual_sentiment_classification(trends, cut = 30):
    elaborated = 0
    sentiment_classification = {}
    for trend in trends:
        elaborated += 1
        classification = input('Classify the trend: ' + str(trend) + ' occurred ' + str(trends[trend]) + 
        ''' times, choosing between:
        0 - Ambiguous | 1 - Happiness | 2 - Anger | 3 - Apprehension | 4 - Information - Sport | 
        5 - Information - Politic | 6 - Information - Entertainment | 7 - Information - Other | 8 - Fear
        => ''')
        if(classification == '1'): sentiment = 'Happiness'
        elif(classification == '2'): sentiment = 'Anger'
        elif(classification == '3'): sentiment = 'Apprehension'
        elif(classification == '4'): sentiment = 'Information - Sport'
        elif(classification == '5'): sentiment = 'Information - Politic'
        elif(classification == '6'): sentiment = 'Information - Entertainment'
        elif(classification == '7'): sentiment = 'Information - Other'
        elif(classification == '8'): sentiment = 'Fear'
        else: 
            print('Invalid value, trend skipped')
            continue
        if sentiment in sentiment_classification: sentiment_classification[sentiment] += 1
        else: sentiment_classification[sentiment] = 1
        if(elaborated == cut): break

    return sentiment_classification


# Main part of the searsen analyzer, use the above functions to compute results
client = MongoClient('mongodb://127.0.0.1:27017')
db = client.searsendb_us

result = db.trends.find()
google = catalog_trends(result, 'google')
result = db.trends.find()
twitter = catalog_trends(result, 'twitter')
result = db.trends.find()
wikipedia = catalog_trends(result, 'wikipedia')
result = db.trends.find()
twitter_google = catalog_trends(result, 'twitter-google')
result = db.trends.find()
twitter_wikipedia = catalog_trends(result, 'twitter-wikipedia')
result = db.trends.find()
google_wikipedia = catalog_trends(result, 'google-wikipedia')
result = db.trends.find()
google_twitter_wikipedia = catalog_trends(result, 'google-twitter-wikipedia')

print('''
*************** SEARSEN ***************
Automatic trend and sentiment dataset analyzer
''')

# Manually classify the 50 most famous trends in each group
google_classified = manual_sentiment_classification(google, 50)
twitter_classified = manual_sentiment_classification(twitter, 50)
wikipedia_classified = manual_sentiment_classification(wikipedia, 50)
twitter_google_classified = manual_sentiment_classification(twitter_google, 50)
twitter_wikipedia_classified = manual_sentiment_classification(twitter_wikipedia, 50)
google_wikipedia_classified = manual_sentiment_classification(google_wikipedia, 50)
google_twitter_wikipedia_classified = manual_sentiment_classification(google_twitter_wikipedia, 50)

#print('\nGOOGLE:\n' + str(google))
#print('\nTWITTER:\n' + str(twitter))
#print('\nWIKIPEDIA:\n' + str(wikipedia))
#print('\nTWITTER-GOOGLE:\n' + str(twitter_google))
#print('\nTWITTER-WIKIPEDIA:\n' + str(twitter_wikipedia))
#print('\nGOOGLE-WIKIPEDIA:\n' + str(google_wikipedia))
#print('\nGOOGLE-TWITTER-WIKIPEDIA:\n' + str(google_twitter_wikipedia) + '\n')

print('\nGOOGLE:\n' + str(google_classified))
print('\nTWITTER:\n' + str(twitter_classified))
print('\nWIKIPEDIA:\n' + str(wikipedia_classified))
print('\nTWITTER-GOOGLE:\n' + str(twitter_google_classified))
print('\nTWITTER-WIKIPEDIA:\n' + str(twitter_wikipedia_classified))
print('\nGOOGLE-WIKIPEDIA:\n' + str(google_wikipedia_classified))
print('\nGOOGLE-TWITTER-WIKIPEDIA:\n' + str(google_twitter_wikipedia_classified))


