# Matching criteria, always keep the original elements of the first list in input which match the second list

import difflib
import re

# Process the trends to be easily comparable, keeping the original strings
def text_processing(trend_list):
    processed_list = []
    if(not isinstance(trend_list, list)): return []
    for trend in trend_list:
        processed_trend = {}
        processed_trend['original'] = trend
        re.sub(' +', ' ', trend) # Remove multiple spaces (redundant, but useful to keep the single spaces if needed)
        processed_trend['processed'] = trend.lower().replace('.', '').replace('-', '').replace('_', '').replace(' ', '')
        processed_list.append(processed_trend)
    return processed_list

# Compare two lists of trends, also accepting partial matches
def lexical_matching(trend_one, trend_two):
    trend_one_processed = text_processing(trend_one)
    trend_two_processed = text_processing(trend_two)
    matches = list({x['original'] for x in trend_one_processed for y in trend_two_processed if x['processed'] in y['processed'] or y['processed'] in x['processed']})
    
    if(len(matches) == 0): return 'No matches'
    return matches

# Compare two lists of trends using the difflib library (no text processing required)
def difflib_matching(trend_one, trend_two):
    if(not isinstance(trend_one, list) or not isinstance(trend_two, list)): return 'No matches'
    threshold = 0.7
    matches = list({x for x in trend_one for y in trend_two if difflib.SequenceMatcher(None, x, y).ratio() > threshold})
    
    if(len(matches) == 0): return 'No matches'
    return matches

# Compare two lists of trends using a semantic approach TODO 
def semantic_matching(trend_one, trend_two):  
    trend_one_processed = text_processing(trend_one)
    trend_two_processed = text_processing(trend_two) 
    return

# Build a dictionary with the matches between each combination of the three sources using the above functions
def get_all_matches(google_trending, twitter_trending, wikipedia_trending):
    matches = {}
    # Lexical matching seems to be the best for a list of keywords and hashtags
    main_match = lexical_matching(twitter_trending, google_trending)
    matches['twitter-google'] = main_match
    matches['google-wikipedia'] = lexical_matching(google_trending, wikipedia_trending)
    matches['twitter-wikipedia'] = lexical_matching(twitter_trending, wikipedia_trending)
    matches['google-twitter-wikipedia'] = lexical_matching(main_match, wikipedia_trending)
    return matches