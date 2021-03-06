# Provide some useful functions to analyze the dataset

from pymongo import MongoClient
import pandas as pd
import numpy as np
import pprint
import seaborn as sns
from collections import OrderedDict
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from keyword_matcher import text_processing
register_matplotlib_converters()

# Check how many consecutive hours each trend was in the trends counting the jumps 
def trend_lifecycle(trends):
    lifecycle = {}
    sources = ['google', 'twitter']
    for i in range(0, trends.count() - 1):
        if i == 0: 
            last_trends_google = []
            last_trends_twitter = []
            last_trends = [[],[]]
        else:
            for keyword in trends[i-1]['google']: last_trends_google.append(keyword)
            for keyword in trends[i-1]['twitter']: last_trends_twitter.append(keyword)
            last_trends = [last_trends_google, last_trends_twitter]

        for n in range(0,2):
            for keyword in trends[i][sources[n]]:
                # If the keyword was trending an hour earlier
                if keyword in last_trends[n]: 
                    # The keyword was already found before for sure
                    lifecycle[keyword]['current_life'] += 1
                    if lifecycle[keyword]['current_life'] > lifecycle[keyword]['max_life']:
                        lifecycle[keyword]['max_life'] = lifecycle[keyword]['current_life']

                # If the keyword wasn't trending an hour earlier
                else: 
                    # If the keyword was already found before
                    if keyword in lifecycle:
                        lifecycle[keyword]['jumps'] += 1
                    # If the keyword is a new trend
                    else: 
                        lifecycle[keyword] = {}
                        lifecycle[keyword]['jumps'] = 0
                        lifecycle[keyword]['max_life'] = 1
                    lifecycle[keyword]['current_life'] = 1

        last_trends_google.clear()
        last_trends_twitter.clear()
        last_trends.clear()

    # Order by max life
    lifecycle = OrderedDict(sorted(lifecycle.items(), key=lambda i: i[1]['max_life']))
    return lifecycle

# Build a dictionary with the first arrival of each trend without using any matching criteria
def trend_first_appearence(trends):
    first_arrival = {
        'google': 0,
        'twitter': 0,
        'wikipedia': 0,
        'google-keywords': [],
        'twitter-keywords': [],
        'wikipedia-keywords': []
    }
    appeared_trends = []
    document_number = 0

    while True:
        trends = db.trends.find(no_cursor_timeout=True).skip(document_number)

        try:
            for document in trends:
                print('Processing document number ' + str(document_number + 1))
                # Ordered by data update times
                for twitter_trend in text_processing(document['twitter']):
                    if twitter_trend['processed'] not in appeared_trends and trend_alltime_existence(twitter_trend['processed'], 'twitter') and not trend_contemporary_existence(document, twitter_trend['processed'], 'twitter'): 
                        first_arrival['twitter'] += 1
                        first_arrival['twitter-keywords'].append(twitter_trend['original'])
                        appeared_trends.append(twitter_trend['processed'])
                        print('Added to Twitter')
                for google_trend in text_processing(document['google']):
                    if google_trend['processed'] not in appeared_trends and trend_alltime_existence(google_trend['processed'], 'google') and not trend_contemporary_existence(document, google_trend['processed'], 'google'): 
                        first_arrival['google'] += 1
                        first_arrival['google-keywords'].append(google_trend['original'])
                        appeared_trends.append(google_trend['processed'])
                        print('Added to Google')
                for wikipedia_trend in text_processing(document['wikipedia']):
                    if wikipedia_trend['processed'] not in appeared_trends and trend_alltime_existence(wikipedia_trend['processed'], 'wikipedia') and not trend_contemporary_existence(document, wikipedia_trend['processed'], 'wikipedia'): 
                        first_arrival['wikipedia-keywords'].append(wikipedia_trend['original'])
                        first_arrival['wikipedia'] += 1
                        appeared_trends.append(wikipedia_trend['processed'])
                        print('Added to Wikipedia')
                document_number += 1
            trends.close()
            break

        except: print("Cursor lost, retrying with skip")

    return first_arrival

# Verify the existence of a trend of a source in the other two sources in the entire dataset
def trend_alltime_existence(trend, source):
    exists = False
    result = db.trends.find(no_cursor_timeout=True)
    sources = ['google', 'twitter', 'wikipedia']
    sources.remove(source)
    for document in result:
        processed_keywords_1 = text_processing(document[sources[0]])
        processed_keywords_2 = text_processing(document[sources[1]])
        for keyword in processed_keywords_1:
            if keyword['processed'] == trend: exists = True
        for keyword in processed_keywords_2:
            if keyword['processed'] == trend: exists = True
    return exists

# Verify the existence of a trend of a source in the other two sources in the same tuple
def trend_contemporary_existence(document, trend, source):
    exists = False
    sources = ['google', 'twitter', 'wikipedia']
    sources.remove(source)
    processed_keywords_1 = text_processing(document[sources[0]])
    processed_keywords_2 = text_processing(document[sources[1]])
    for keyword in processed_keywords_1:
        if keyword['processed'] == trend: exists = True
    for keyword in processed_keywords_2:
        if keyword['processed'] == trend: exists = True
    return exists

# Estimate the polarization of each keyword
def estimate_total_polarization(trends):
    polarization = {}
    for document in trends:
        if isinstance(document['sentiment expanded'], dict):
            for keyword in document['sentiment expanded']:
                if keyword not in polarization:
                    polarization[keyword] = estimate_polarization(document['sentiment expanded'][keyword])
    return polarization

# Estimate the polarization for a selected keyword
def estimate_polarization(sentiment):
    negative = 0
    positive = 0
    total = 0
    treshold = 5
    result = {}
    for rate in sentiment:
        total += 1
        if float(rate) >= 0.25: positive += 1
        if float(rate) <= -0.25: negative += 1
    if positive + negative > total // 5 and negative > treshold and positive > treshold: 
        result['description'] = 'Polarized with ' + str(positive) + ' positives and ' + str(negative) + ' negatives'
        result['boolean'] = True
    else: 
        result['description'] = 'Not polarized with ' + str(positive) + ' positives and ' + str(negative) + ' negatives'
        result['boolean'] = False

    result['positives'] = positive
    result['negatives'] = negative
    return result

# Count the number of positive and negative sentiments
def sentiment_count(trends):
    treshold = 20
    sentiments = {}
    sentiments['positive'] = 0
    sentiments['negative'] = 0
    sentiments['neutral'] = 0
    already_processed = []
    for document in trends:
        if isinstance(document['sentiment'], dict):
            for keyword in document['sentiment']:
                if keyword not in already_processed:
                    if int(document['sentiment'][keyword]['value']) > treshold: sentiments['positive'] += 1
                    elif int(document['sentiment'][keyword]['value']) < -treshold: sentiments['negative'] += 1
                    else: sentiments['neutral'] +=1
                    already_processed.append(keyword)

    return sentiments

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
        if source == 'google': matches = document['google']
        elif source == 'twitter': matches = document['twitter']
        elif source == 'wikipedia': matches = document['wikipedia']
        elif source == 'twitter-google': matches = document['matches']['twitter-google']
        elif source == 'twitter-wikipedia': matches = document['matches']['twitter-wikipedia']
        elif source == 'google-wikipedia': matches = document['matches']['google-wikipedia']
        elif source == 'google-twitter-wikipedia': matches = document['matches']['google-twitter-wikipedia']
        else: matches = document['google']

        if isinstance(matches, list) and matches:
            for trend in matches:
                if trend in match_counter: match_counter[trend] += 1
                else: match_counter[trend] = 1

    # Sort by descending value
    match_counter = {k: v for k, v in sorted(match_counter.items(), key=lambda item: item[1], reverse=True)}
    return match_counter

# Accept a catalogued trend list, take the first n trends and let the user assign them to a class
def manual_classification(trends, classes, amount, cut = 30, sentiment = {}):
    elaborated = 0
    classification = {}
    print('Available classes:')
    for i in range(0, len(classes)): 
        classification[classes[i]] = 0
        print(str(i) + ' - ' + str(classes[i]))
    print()
    for trend in trends:
        elaborated += 1
        if sentiment: 
            try: print('The detected sentiment for the following trend was: ' + str(sentiment[trend]))
            except: pass
        classified = input('Classify the trend: ' + str(trend) + ', occurred ' + str(trends[trend]) + ' times => ')
        try: trend_class = classes[int(classified)]
        except: 
            print('Invalid value, trend skipped')
            if elaborated == cut: break
            continue
        # Choose to consider the amount of times a trend appeared or not 
        if not amount: classification[trend_class] += 1
        else: classification[trend_class] += trends[trend]
        if elaborated == cut: break

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

# Classify a list of keywords in a set of classes and plot the result
def classify_and_plot(result, cut = 30, amount = False, simple = False):
    # The result has to be taken again from the db for the functions to work
    google = catalog_trends(result, 'google')
    result = db.trends.find()
    twitter = catalog_trends(result, 'twitter')
    result = db.trends.find()
    wikipedia = catalog_trends(result, 'wikipedia')
    if not simple:
        result = db.trends.find()
        twitter_google = catalog_trends(result, 'twitter-google')
        result = db.trends.find()
        twitter_wikipedia = catalog_trends(result, 'twitter-wikipedia')
        result = db.trends.find()
        google_wikipedia = catalog_trends(result, 'google-wikipedia')
        result = db.trends.find()
        google_twitter_wikipedia = catalog_trends(result, 'google-twitter-wikipedia')

    # Manually classify the n most famous trends in each group
    classes_topics = ['Politic', 'Sport', 'Music', 'Film, TV, Games, Books', 'Death Related', 'Viral Trends', 'Other']
    classes_topics_2 = ['Politic', 'Sport', 'Entertainment', 'Health and Environment', 'Celebrity Death', 'Tech and Economy', 'Other']
    classes_entities = ['Person', 'Animal or Location', 'Event or Trend', 'Object', 'Title and Fictional', 'Disease', 'Group or Team']
    classes_feelings = ['Fear', 'Apprehension', 'Approvation', 'Curiosity', 'Anger', 'Confusion', 'Ambiguous']
    classes_opinions = ['Negative Opinions', 'Polarized Opinions', 'Positive Opinions', 'No Opinion']
    classes_list = [classes_topics, classes_topics_2, classes_entities, classes_feelings, classes_opinions]
    classes = classes_list[2]

    result = db.trends.find(no_cursor_timeout=True)
    sentiment = compute_sentiment(result)

    google_classified = manual_classification(google, classes, amount, cut)
    twitter_classified = manual_classification(twitter, classes, amount, cut)
    wikipedia_classified = manual_classification(wikipedia, classes, amount, cut)
    if not simple:
        twitter_google_classified = manual_classification(twitter_google, classes, amount, cut, sentiment) # Sentiment included
        twitter_wikipedia_classified = manual_classification(twitter_wikipedia, classes, amount, cut)
        google_wikipedia_classified = manual_classification(google_wikipedia, classes, amount, cut)
        google_twitter_wikipedia_classified = manual_classification(google_twitter_wikipedia, classes, amount, cut)
        classified_dicts = [google_classified, twitter_classified, wikipedia_classified, twitter_google_classified,
                    twitter_wikipedia_classified, google_wikipedia_classified, google_twitter_wikipedia_classified]
    else: classified_dicts = [google_classified, twitter_classified, wikipedia_classified]

    # Generate a plot with the different classes and groups
    if not simple: N = 7
    else: N = 3
    class_one_values = np.array(get_multi_dictionary_values(classified_dicts, classes[0]))
    class_two_values = np.array(get_multi_dictionary_values(classified_dicts, classes[1]))
    class_three_values = np.array(get_multi_dictionary_values(classified_dicts, classes[2]))
    class_four_values = np.array(get_multi_dictionary_values(classified_dicts, classes[3]))
    class_five_values = np.array(get_multi_dictionary_values(classified_dicts, classes[4]))
    class_six_values = np.array(get_multi_dictionary_values(classified_dicts, classes[5]))
    class_seven_values = np.array(get_multi_dictionary_values(classified_dicts, classes[6]))
    #class_eight_values = np.array(get_multi_dictionary_values(classified_dicts, classes[7]))
    #class_nine_values = np.array(get_multi_dictionary_values(classified_dicts, classes[8]))
    ind = np.arange(N)
    width = 0.7

    # Set the color
    palette = sns.color_palette('muted', len(classes))
    p1 = plt.bar(ind, class_one_values, width, color=palette[0])
    p2 = plt.bar(ind, class_two_values, width, bottom=class_one_values, color=palette[1])
    p3 = plt.bar(ind, class_three_values, width, bottom=class_one_values + class_two_values, color=palette[2])
    p4 = plt.bar(ind, class_four_values, width, bottom=class_one_values + class_two_values + class_three_values, color=palette[3])
    p5 = plt.bar(ind, class_five_values, width, bottom=class_one_values + class_two_values + class_three_values + class_four_values, color=palette[4])
    p6 = plt.bar(ind, class_six_values, width, bottom=class_one_values + class_two_values + class_three_values + class_four_values + class_five_values, color=palette[5])
    p7 = plt.bar(ind, class_seven_values, width, bottom = class_one_values + class_two_values + class_three_values + class_four_values + class_five_values + class_six_values, color=palette[6])
    #p8 = plt.bar(ind, class_eight_values, width, bottom = class_one_values + class_two_values + class_three_values + class_four_values + class_five_values + class_six_values + class_seven_values, color=palette[7])
    #p9 = plt.bar(ind, class_nine_values, width, bottom = class_one_values + class_two_values + class_three_values + class_four_values + class_five_values + class_six_values + class_seven_values + class_eight_values, color=palette[8])

    plt.ylabel('Trends Processed')
    plt.title('Classification')
    if not simple: plt.xticks(ind, ('Google', 'Twitter', 'Wikipedia', 'Twi-Goo', 'Twi-Wiki', 'Goo-Wiki', 'Goo-Twi-Wiki'))
    else: plt.xticks(ind, ('Google', 'Twitter', 'Wikipedia'))
    if not amount: plt.yticks(np.arange(0, cut+6, 5))
    plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0], p6[0], p7[0]), (classes[0], classes[1], classes[2], classes[3], classes[4], classes[5], classes[6]))

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

# Available datasets
db = client.searsendb_us
#db = client.searsendb_it
#db = client.searsendb_it_precorona

result = db.trends.find(no_cursor_timeout=True)
pp = pprint.PrettyPrinter(indent=4)

analysis = input('''
Choose the analysis: 
0 - classify and plot basic
1 - classify and plot complete
2 - classify and plot complete with amount
3 - trend lifecycle 
4 - trend polarization
5 - trend first appearence
6 - total sentiment count
=> ''')

if int(analysis) == 0:
    # Manually classify the n most famous trends of the main source only)
    classify_and_plot(result, 50, False, True)
elif int(analysis) == 1:
    # Manually classify the n most famous trends
    classify_and_plot(result, 50)
elif int(analysis) == 2:
    # Manually classify the n most famous trends counting the amount of times they were in the trends
    classify_and_plot(result, 50, True)
elif int(analysis) == 3:
    # Evaluate the lifecycle of each trend
    lifecycle = trend_lifecycle(result)
    pp.pprint(lifecycle)
    print('\nComputed the lifecycle of ' + str(len(lifecycle)) + ' keywords')
elif int(analysis) == 4:
    # Estimate the polarization for each collected trend
    polarization = estimate_total_polarization(result)
    total = len(polarization)
    polarized = 0
    for keyword in polarization:
        if polarization[keyword]['boolean']: 
            polarized += 1
            print(keyword)
    print('\n' + str(polarized) + ' keywords out of ' + str(total) + ' unique keywords are polarized')
elif int(analysis) == 5:
    # Estimate the first arrival of each trend found in 2 or more sources (no keyword matching)
    appearences = trend_first_appearence(result)
    print(appearences)
elif int(analysis) == 6:
    # Evaluate the number of positive and negative sentiment for each query
    sentiment_count = sentiment_count(result)
    print(str(sentiment_count['positive']) + ' positive sentiments, ' + str(sentiment_count['negative']) + ' negative sentiments and ' + str(sentiment_count['neutral']) + ' neutral')
else:
    print('Nothing to do here!')
result.close()