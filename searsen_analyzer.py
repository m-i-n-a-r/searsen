# Provide some useful functions to analyze the dataset

from pymongo import MongoClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from keyword_matcher import text_processing
register_matplotlib_converters()

# Check how many consecutive hours each trend was in the trends counting the jumps TODO 
def trend_lifecycle(trends):
    lifecycle = {}
    counting = 0
    for trend in trends:
        for keyword in trend['google']:
            if keyword in lifecycle and counting == 1: lifecycle[keyword]['max_life'] += 1
            elif keyword in lifecycle and counting == 0: 
                lifecycle[keyword]['max_life'] = 1
                counting = 1
            else: lifecycle[keyword] = 1
        for keyword in trend['twitter']:
            continue
    return lifecycle

# Build a dictionary with the first arrival of each trend
def trend_first_appearence(trends):
    first_arrival = {
        'Google': 0,
        'Twitter': 0,
        'Wikipedia': 0
    }
    appeared_trends = []
    for trend in trends:
        for google_trend in text_processing(trend['google'])['processed']:
            if google_trend not in appeared_trends and trend_existence(trends, google_trend, 'google'): 
                first_arrival['Google'] += 1
        for twitter_trend in text_processing(trend['twitter'])['processed']:
            if twitter_trend not in appeared_trends and trend_existence(trends, twitter_trend, 'twitter'): 
                first_arrival['Twitter'] += 1
        for wikipedia_trend in text_processing(trend['wikipedia'])['processed']:
            if wikipedia_trend not in appeared_trends and trend_existence(trends, wikipedia_trend, 'wikipedia'): 
                first_arrival['Wikipedia'] += 1

    return first_arrival

# Verify the existence of a trend of a source in the other two sources
def trend_existence(trends, trend, source):
    return

# Estimate the polarization for a selected keyword
def estimate_polarization(sentiment):
    polarized = {}
    negative = 0
    positive = 0
    total = 0
    treshold = 10
    for keyword in sentiment:
        for rate in sentiment:
            total += 1
            if rate >= 0.5: positive += 1
            if rate <= -0.5: negative += 1
        if positive + negative > total // 2 and negative > treshold and positive > treshold: 
            result = 'Polarized with ' + str(positive) + ' positives and ' + str(negative) + 'negatives'
        else: result = 'Not polarized'
        polarized[keyword] = result
        
    return polarized

# Compute the mean value of the sentiment collected on a certain trend
def compute_sentiment(trends):
    sentiment_computed = {}
    for document in trends:
        sentiment = document['sentiment']
        if isinstance(sentiment, dict):
             for trend in sentiment: sentiment_computed[trend] = sentiment[trend]
    
    return sentiment_computed

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
def manual_classification(trends, classes, cut = 30, sentiment = {}):
    elaborated = 0
    classification = {}
    print('Available classes:')
    for i in range(0, len(classes)): 
        classification[classes[i]] = 0
        print(str(i) + ' - ' + str(classes[i]))
    print()
    for trend in trends:
        elaborated += 1
        if(sentiment): 
            try: print('The detected sentiment for the following trend was: ' + str(sentiment[trend]))
            except: pass
        classified = input('Classify the trend: ' + str(trend) + ', occurred ' + str(trends[trend]) + ' times => ')
        try: trend_class = classes[int(classified)]
        except: 
            print('Invalid value, trend skipped')
            if(elaborated == cut): break
            continue
        classification[trend_class] += 1
        if(elaborated == cut): break

    print('\nClassified ' + str(elaborated) + ' trends.')
    return classification

# Get a list containing the values of a single key across multiple dictionaries
def get_multi_dictionary_values(dicts, key_name):
    values = []
    for dict in dicts:
        for key in dict:
            if key == key_name:
                values.append(dict[key])
    return values

def classify_and_plot(result):
    # The result has to be taken again from the db for the functions to work
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

    # Manually classify the n most famous trends in each group
    cut = 40
    classes_topics = ['Politic', 'Sport', 'Music', 'Film, TV, Games', 'Death Related', 'Other']
    #classes_feelings = ['Fear', 'Apprehension', 'Approvation', 'Curiosity', 'Anger', 'Ambiguous']
    #classes_opinions = ['Negative', 'Polarized Opinions', 'Positive Opinions', 'No Opinion']
    classes = classes_topics

    result = db.trends.find()
    sentiment = compute_sentiment(result)

    google_classified = manual_classification(google, classes, cut)
    twitter_classified = manual_classification(twitter, classes, cut)
    wikipedia_classified = manual_classification(wikipedia, classes, cut)
    twitter_google_classified = manual_classification(twitter_google, classes, cut, sentiment) # Sentiment included
    twitter_wikipedia_classified = manual_classification(twitter_wikipedia, classes, cut)
    google_wikipedia_classified = manual_classification(google_wikipedia, classes, cut)
    google_twitter_wikipedia_classified = manual_classification(google_twitter_wikipedia, classes, cut)
    classified_dicts = [google_classified, twitter_classified, wikipedia_classified, twitter_google_classified,
                    twitter_wikipedia_classified, google_wikipedia_classified, google_twitter_wikipedia_classified]

    # Generate a plot with the different classes and groups
    N = 7
    class_one_values = np.array(get_multi_dictionary_values(classified_dicts, classes[0]))
    class_two_values = np.array(get_multi_dictionary_values(classified_dicts, classes[1]))
    class_three_values = np.array(get_multi_dictionary_values(classified_dicts, classes[2]))
    class_four_values = np.array(get_multi_dictionary_values(classified_dicts, classes[3]))
    class_five_values = np.array(get_multi_dictionary_values(classified_dicts, classes[4]))
    class_six_values = np.array(get_multi_dictionary_values(classified_dicts, classes[5]))
    #class_seven_values = np.array(get_multi_dictionary_values(classified_dicts, classes[6]))
    #class_eight_values = np.array(get_multi_dictionary_values(classified_dicts, classes[7]))
    #class_nine_values = np.array(get_multi_dictionary_values(classified_dicts, classes[8]))
    ind = np.arange(N)
    width = 0.6

    p1 = plt.bar(ind, class_one_values, width)
    p2 = plt.bar(ind, class_two_values, width, bottom = class_one_values)
    p3 = plt.bar(ind, class_three_values, width, bottom = class_one_values + class_two_values)
    p4 = plt.bar(ind, class_four_values, width, bottom = class_one_values + class_two_values + class_three_values)
    p5 = plt.bar(ind, class_five_values, width, bottom = class_one_values + class_two_values + class_three_values +class_four_values)
    p6 = plt.bar(ind, class_six_values, width, bottom = class_one_values + class_two_values + class_three_values +class_four_values + class_five_values)
    #p7 = plt.bar(ind, class_seven_values, width, bottom = class_one_values + class_two_values + class_three_values +class_four_values + class_five_values + class_six_values)
    #p8 = plt.bar(ind, class_eight_values, width, bottom = class_one_values + class_two_values + class_three_values +class_four_values + class_five_values + class_six_values + class_seven_values)
    #p9 = plt.bar(ind, class_nine_values, width, bottom = class_one_values + class_two_values + class_three_values +class_four_values + class_five_values + class_six_values + class_seven_values + class_eight_values)

    plt.ylabel('Examined Trends')
    plt.title('Classification on a 250 hours dataset')
    plt.xticks(ind, ('Google', 'Twitter', 'Wikipedia', 'Twi-Goo', 'Twi-Wiki',
                     'Goo-Wiki', 'Goo-Twi-Wiki'))
    plt.yticks(np.arange(0, 46, 5))
    plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0], p6[0]), 
                (classes[0], classes[1], classes[2], classes[3], classes[4], classes[5]))

    plt.show()

    #print('\nGOOGLE:\n' + str(google))
    #print('\nTWITTER:\n' + str(twitter))
    #print('\nWIKIPEDIA:\n' + str(wikipedia))
    #print('\nTWITTER-GOOGLE:\n' + str(twitter_google))
    #print('\nTWITTER-WIKIPEDIA:\n' + str(twitter_wikipedia))
    #print('\nGOOGLE-WIKIPEDIA:\n' + str(google_wikipedia))
    #print('\nGOOGLE-TWITTER-WIKIPEDIA:\n' + str(google_twitter_wikipedia) + '\n')

    #print('\nGOOGLE:\n' + str(google_classified))
    #print('\nTWITTER:\n' + str(twitter_classified))
    #print('\nWIKIPEDIA:\n' + str(wikipedia_classified))
    #print('\nTWITTER-GOOGLE:\n' + str(twitter_google_classified))
    #print('\nTWITTER-WIKIPEDIA:\n' + str(twitter_wikipedia_classified))
    #print('\nGOOGLE-WIKIPEDIA:\n' + str(google_wikipedia_classified))
    #print('\nGOOGLE-TWITTER-WIKIPEDIA:\n' + str(google_twitter_wikipedia_classified))


# Main part of the searsen analyzer, use the above functions to compute results
print('''
*************** SEARSEN ***************
Automatic trend and sentiment dataset analyzer
''')
client = MongoClient('mongodb://127.0.0.1:27017')
db = client.searsendb_us
result = db.trends.find()

analysis = input('Choose the analysis: 1 for classify and plot, 2 for trend first appearence => ')

if int(analysis) == 1:
    # Manually classify the most famous trends and plot the result
    classify_and_plot(result)
elif int(analysis) == 2:
    # Estimate the first arrival of each trend found in 2 or more sources
    trend_first_appearence(result)
else:
    print('Nothing to do here!')
