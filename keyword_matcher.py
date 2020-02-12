# Matching criteria, always keep the original elements of the first list in input which match the second list

import difflib
import re
import tagme
import seaborn as sns
import numpy as np
from fuzzywuzzy import fuzz
from sematch.semantic.similarity import WordNetSimilarity
from searsen_credentials import tagme_token
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

tagme.GCUBE_TOKEN = tagme_token

# Process the trends to be easily comparable, keeping the original strings
def text_processing(trend_list, keep_spaces = False):
    processed_list = []
    if not isinstance(trend_list, list): return []
    for trend in trend_list:
        processed_trend = {}
        processed_trend['original'] = trend
        trend = re.sub(' +', ' ', trend) # Remove multiple spaces (redundant, but useful to keep the single spaces if needed)
        # Keep the spaces in the smartest way possible
        if keep_spaces == True: 
            a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
            trend = a.sub(r' \1', trend).lower()
            trend = re.sub(' +', ' ', trend)
            processed_trend['processed'] = trend.replace('.', ' ').replace('-', ' ').replace('_', ' ')
        else: processed_trend['processed'] = trend.lower().replace('.', '').replace('-', '').replace('_', '').replace(' ', '')
        processed_list.append(processed_trend)
    return processed_list

# Naive matching based on a simple list intersection
def naive_matching(trend_one, trend_two):
    trend_one_processed = text_processing(trend_one)
    trend_two_processed = text_processing(trend_two)
    matches = list({x['original'] for x in trend_one_processed for y in trend_two_processed if x['processed'] == y['processed']})

    if len(matches) == 0: return 'No matches'
    return matches

# Compare two lists of trends using an euristic, also accepting partial matches
def syntactic_matching(trend_one, trend_two):
    trend_one_processed = text_processing(trend_one)
    trend_two_processed = text_processing(trend_two)
    matches = list({x['original'] for x in trend_one_processed for y in trend_two_processed if x['processed'] in y['processed'] or y['processed'] in x['processed']})
    
    if len(matches) == 0: return 'No matches'
    return matches

# Compare two lists of trends using the fuzzy distances
def fuzzy_matching(trend_one, trend_two, threshold = 90):
    matches = []
    trend_one_processed = text_processing(trend_one, keep_spaces = True)
    trend_two_processed = text_processing(trend_two, keep_spaces = True)
    for keyword_one in trend_one_processed:
        for keyword_two in trend_two_processed:
            if(fuzz.ratio(keyword_one['processed'], keyword_two['processed']) > threshold or 
            fuzz.partial_ratio(keyword_one['processed'], keyword_two['processed']) > threshold or
            fuzz.token_sort_ratio(keyword_one['processed'], keyword_two['processed']) > threshold):
                matches.append(keyword_one['original'])

    if len(matches) == 0: return 'No matches'
    return list(set(matches))

# Compare two lists of trends using the difflib library (no text processing required)
def sequence_matching(trend_one, trend_two, threshold = 0.5):
    if not isinstance(trend_one, list) or not isinstance(trend_two, list): return 'No matches'
    matches = list({x for x in trend_one for y in trend_two if difflib.SequenceMatcher(None, x, y).ratio() > threshold})
    
    if len(matches) == 0: return 'No matches'
    return matches

# Compare two lists of trends using a semantic approach
def semantic_matching(trend_one, trend_two):  
    treshold = 0.3
    trend_one_processed = text_processing(trend_one, keep_spaces = True)
    trend_two_processed = text_processing(trend_two, keep_spaces = True)
    # The options are Wordnet, YAGO and DBpedia (only the first seems usable)
    wns = WordNetSimilarity()
    matches = list({x['original'] for x in trend_one_processed for y in trend_two_processed 
                    if wns.word_similarity(x['processed'], y['processed'], 'li') > treshold})
    
    if len(matches) == 0: return 'No matches'
    return matches

# Compare two lists of trends using Tagme annotations TODO doesn't work as expected
def tagme_matching(trend_one, trend_two):
    matches = []
    trend_one_processed = text_processing(trend_one, keep_spaces = True)
    trend_two_processed = text_processing(trend_two, keep_spaces = True)

    for keyword_one in trend_one_processed:
        for keyword_two in trend_two_processed:
            relations = tagme.relatedness_title((keyword_one['processed'], keyword_two['processed']))
            print('Comparing ' + keyword_one['processed'] + ' and ' + keyword_two['processed'])
            if relations.relatedness[0].rel and int(relations.relatedness[0].rel) > 0: matches.append(keyword_one['original'])

    if len(matches) == 0: return 'No matches'
    return matches

# Compare two lists of trends using an euristic, the fuzzy distances and some particular conditions based on domain knowledge
def hybrid_matching(trend_one, trend_two):
    trend_one_processed = text_processing(trend_one)
    trend_two_processed = text_processing(trend_two)
    matches = list({x['original'] for x in trend_one_processed for y in trend_two_processed 
                    if (x['processed'] in y['processed'] or y['processed'] in x['processed']) and
                    ((len(x['original']) == len(y['original']) < 4 or (len(x['original']) > 3 and len(y['original']) > 3)))})
    
    matches_fuzzy = fuzzy_matching(trend_one, trend_two)
    matches = list(set().union(matches, matches_fuzzy))

    if len(matches) == 0: return 'No matches'
    return matches

# Build a dictionary with the matches between each combination of the three sources using the above functions
def get_all_matches(google_trending, twitter_trending, wikipedia_trending):
    matches = {}
    # Syntactic matching seems to be the best for a list of keywords and hashtags
    main_match = hybrid_matching(twitter_trending, google_trending)
    matches['twitter-google'] = main_match
    matches['google-wikipedia'] = hybrid_matching(google_trending, wikipedia_trending)
    matches['twitter-wikipedia'] = hybrid_matching(twitter_trending, wikipedia_trending)
    matches['google-twitter-wikipedia'] = hybrid_matching(main_match, wikipedia_trending)
    return matches

# Compute the metrics (precision, recall, f-measure) for a given result of a matching algorithm
def compute_metrics(result, matches):
    exact = 0
    false_positives = 0
    false_negatives = 0
    for word in result:
        if word in matches: exact += 1
        else: false_positives += 1

    false_negatives = len(matches) - exact + false_positives
    if false_negatives > 20: false_negatives = 20
    print('Exact Matches: ' + str(exact) + ' | False Positives: ' + str(false_positives) + ' | False Negatives: ' + str(false_negatives))
    performance_percentage = (exact * 5) - (5 * false_positives)
    # Compute the data for plots etc.
    data = {}
    precision = exact / (exact + false_positives)
    recall = exact / (exact + false_negatives)
    data['exact'] = exact
    data['false positives'] = false_positives
    data['false negatives'] = false_negatives
    data['percentage'] = performance_percentage
    data['precision'] = precision
    data['recall'] = recall
    data['f-measure'] = (2 * precision * recall) / (precision + recall)
    return data

# Plot the ROC curve
def plot_roc_curve(data):
    false_pos_rate = []
    true_pos_rate = []
    thresholds = np.arange(0.0, 1.01, .05)
    for i in range (0, len(thresholds)):
        true_positives = data[i]['exact']
        false_positives = data[i]['false positives']
        false_pos_rate.append(false_positives/float(max(len(list_one), len(list_two))))
        true_pos_rate.append(true_positives/float(len(matches)))

    cmap = sns.cubehelix_palette(8, start=.5, rot=-.75, dark=0.2, light=0.5, as_cmap=True)
    fig, ax = plt.subplots()
    fig.suptitle('ROC Curve', fontsize=18)
    plt.axis('scaled')
    plt.rcParams['axes.grid'] = True
    plt.grid(True, zorder=1)
    plt.xticks(np.arange(0, 1.1, 0.1))
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.xlabel('False Positive Rate', fontsize=14)
    plt.ylabel('True Positives Rate', fontsize=14)
    plt.plot(false_pos_rate, true_pos_rate, color="grey", zorder=2)
    points = ax.scatter(false_pos_rate, true_pos_rate, c=thresholds, s=60, cmap=cmap, zorder=3)
    cbar = fig.colorbar(points)
    cbar.set_label('Treshold', rotation=90)
    cbar.set_ticks([0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00])
    cbar.set_ticklabels(['0.00', '0.05', '0.10', '0.15', '0.20', '0.25', '0.30', '0.35', '0.40', '0.45', '0.50', '0.55', '0.60', '0.65', '0.70', '0.75', '0.80', '0.85', '0.90', '0.95', '1.00'])
    plt.show()

# Plot the Precision-Recall curve
def plot_precision_recall_curve(data):
    precisions = []
    recalls = []
    thresholds = np.arange(0.0, 1.01, .05)
    for i in range (0, len(thresholds)):
        precision = data[i]['precision']
        recall = data[i]['recall']
        precisions.append(precision)
        recalls.append(recall)

    cmap = sns.cubehelix_palette(8, start=.5, rot=-.75, dark=0.1, light=0.6, as_cmap=True)
    fig, ax = plt.subplots()
    fig.suptitle('Precision-Recall Curve', fontsize=18)
    plt.axis('scaled')
    plt.rcParams['axes.grid'] = True
    plt.grid(True, zorder=1)
    plt.xticks(np.arange(0, 1.1, 0.1))
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.xlabel('Precision', fontsize=14)
    plt.ylabel('Recall', fontsize=14)
    plt.plot(precisions, recalls, color="grey", zorder=2)
    points = ax.scatter(precisions, recalls, c=thresholds, s=60, cmap=cmap, zorder=3)
    cbar = fig.colorbar(points)
    cbar.set_label('Treshold', rotation=90)
    cbar.set_ticks([0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00])
    cbar.set_ticklabels(['0.00', '0.05', '0.10', '0.15', '0.20', '0.25', '0.30', '0.35', '0.40', '0.45', '0.50', '0.55', '0.60', '0.65', '0.70', '0.75', '0.80', '0.85', '0.90', '0.95', '1.00'])
    plt.show()


# Avoid to run the script when imported
if __name__ == '__main__':
    # Quick tests with two lists containing every possible difficulty
    print('''
*************** SEARSEN ***************
Automatic keyword matching module
''')


    analysis = input('''
Choose the analysis: 
1 - complete test on every algorithm
2 - ROC and P-R curves, sequence matching
3 - ROC and P-R curves, fuzzy matching
=> ''')
    
    list_one = ["GRAMMYs","RoyalRumble","Bolton","Kobe","RIPMamba","Edge","Ariana","Lana","Demi Lovato","AOTY",
    "Lesnar","Old Town Road","keith lee","Marss","Letter to Nipsey","Namjoon","Igor","Record of the Year",
    "WrestleMania","DJ Khaled","Rated RKO","mondaythoughts","H.E.R.","Bonnie Raitt","Altobelli","Gary Clark Jr.",
    "Finneas","sharon osbourne","Kim Taehyung","Christopher Cross","I Sing the Body Electric","Misty Copeland",
    "Rockwell","Christina Mauser","Persona vs IRL","Stan Wawrinka","SOTY","Ricochet","Smokey Robinson","esam",
    "HiltonSweepstakes","ReleaseManzoorPashteen","itshardtofeellike","MySexySunday","albumoftheyear", "Coronavirus",
    "NCIS","EMA","HCI","China","HappyLunarNewYear","ChrisWattsConfessions","Joe Rogan","Mr. Bean","Ms. Jackson",
    "horse","Impeachment","Panda","helicoptercrash","Hilary Clinton","Virginia","Gun Rally","World Cup Results"]
    
    list_two = ["Kobe Bryant","Kobe Bryant dead","Kobe Bryant kids","Billie Eilish","Royal Rumble 2020",
    "Tanya Tucker","Kareem Abdul-Jabbar","Alison Morris","Steven Tyler","Demi Lovato","Camila Cabello",
    "Tyler, the Creator","Gwen Stefani","Prince","Grammys 2020 date and time","S-76 helicopter","Lil Nas X",
    "Celtics","Rosalia","Christina Mauser", "Corona Virus Symptoms", "ncis", "European Medicine Agency",
    "Seth Cilessen","China Export","Lunar New Year","Chris Watts","Joe Rogan","Mr Bean","Miss Jackson","ema",
    "zebra","Trump Impeachment","Panda Bear","Helicopter Crashes","Hilary Clinton","Virginia Gun Rally","Results Election"]

    matches = ["Demi Lovato", "GRAMMYs", "RoyalRumble", "Kobe", "Christina Mauser", "Coronavirus", "NCIS",
    "EMA", "China", "HappyLunarNewYear", "ChrisWattsConfessions", "Joe Rogan", "Mr. Bean", "Ms. Jackson",
    "Impeachment", "Panda", "helicoptercrash", "Hilary Clinton", "Virginia", "Gun Rally"]
 
    if int(analysis) == 1:
        print('\nSemantic Matching:')
        semantic = semantic_matching(list_one, list_two)
        data_semantic = compute_metrics(semantic, matches)
    
        #print('\nTagme matching:')
        #tagme = tagme_matching(list_one, list_two)
        #data_tagme = compute_metrics(tagme, matches)
    
        print('\nNaive Matching:')
        naive = naive_matching(list_one, list_two)
        data_naive = compute_metrics(naive, matches)
    
        print('\nSequence Matching:')
        sequence = sequence_matching(list_one, list_two)
        data_sequence = compute_metrics(sequence, matches)

        print('\nSyntactic Matching:')
        syntactic = syntactic_matching(list_one, list_two)
        data_syntactic = compute_metrics(syntactic, matches)
    
        print('\nFuzzy Matching:')
        fuzzy = fuzzy_matching(list_one, list_two)
        data_fuzzy = compute_metrics(fuzzy, matches)
    
        print('\nHybrid Matching:')
        hybrid = hybrid_matching(list_one, list_two)
        data_hybrid = compute_metrics(hybrid, matches)
    
        print('\nNUMBER OF MATCHINGS FOR THE TEST LISTS: ' + str(len(matches)) + '\n')
    
    elif int(analysis) == 2:
        aggregated_data_sequence = []
        for i in range(0,101,5):
            threshold = i / 100
            if threshold == 1: threshold = 0.99
            print('\nSequence Matching, threshold: ' + str(threshold))
            sequence = sequence_matching(list_one, list_two, threshold)
            data_sequence = compute_metrics(sequence, matches)
            aggregated_data_sequence.append(data_sequence)
        plot_roc_curve(aggregated_data_sequence)
        plot_precision_recall_curve(aggregated_data_sequence)

    elif int(analysis) == 3:
        aggregated_data_fuzzy = []
        for i in range(0,101,5):
            threshold = i
            if threshold == 100: threshold = 99
            print('\nFuzzy Matching, threshold: ' + str(threshold))
            fuzzy = fuzzy_matching(list_one, list_two, threshold)
            data_fuzzy = compute_metrics(fuzzy, matches)
            aggregated_data_fuzzy.append(data_fuzzy) 
        plot_roc_curve(aggregated_data_fuzzy)
        plot_precision_recall_curve(aggregated_data_fuzzy)
    
    else: print('Nothing to do here!')