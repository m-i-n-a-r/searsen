# Provide some useful functions to analyze the dataset

from pymongo import MongoClient

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

    # Sort by value
    match_counter = {k: v for k, v in sorted(match_counter.items(), key=lambda item: item[1])}
    return match_counter


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

print('\nGOOGLE:\n' + str(google))
print('\nTWITTER:\n' + str(twitter))
print('\nWIKIPEDIA:\n' + str(wikipedia))
print('\nTWITTER-GOOGLE:\n' + str(twitter_google))
print('\nTWITTER-WIKIPEDIA:\n' + str(twitter_wikipedia))
print('\nGOOGLE-WIKIPEDIA:\n' + str(google_wikipedia))
print('\nGOOGLE-TWITTER-WIKIPEDIA:\n' + str(google_twitter_wikipedia) + '\n')