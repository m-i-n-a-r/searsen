# Matching criteria, always keep the original elements of the first list in input which match the second list

import difflib

# Process the trends to be easily comparable, keeping the original strings
def text_processing(trend_list):
    processed_dict = {}
    processed_dict['processed'] = [trend.lower().replace(' ', '.').replace('-', '.').replace('_', '.') for trend in trend_list]
    processed_dict['original'] = trend_list
    return processed_dict

# Compare two lists of trends, also accepting partial matches
def lexical_matching(trend_one, trend_two):
    trend_one_processed = text_processing(trend_one)
    trend_two_processed = text_processing(trend_two)
    matches = list({x['original'] for x in trend_one_processed for y in trend_two_processed if x['processed'] in y['processed'] or y['processed'] in x['processed']})

    return matches

# Compare two or three lists of trends using the difflib library
def difflib_matching(google_trending, twitter_trending, wikipedia_trending = None):
    threshold = 0.7
    if(wikipedia_trending is not None):
        matching_trends_first = list({x for x in twitter_trending for y in google_trending if difflib.SequenceMatcher(None, x, y).ratio() > threshold})
        matching_trends = list({x for x in matching_trends_first for y in wikipedia_trending if difflib.SequenceMatcher(None, x, y).ratio() > threshold})
    else:
        matching_trends = list({x for x in twitter_trending for y in google_trending if difflib.SequenceMatcher(None, x, y).ratio() > threshold})
    
    return matching_trends

# Compare two or three lists of trends using a semantic approach TODO
def semantic_matching(trend_one, trend_two):  
    trend_one_processed = text_processing(trend_one)
    trend_two_processed = text_processing(trend_two) 
    return

# Compare two or three lists of trends using all the above approaches TODO
def hybrid_matching(google_trending, twitter_trending, wikipedia_trending = None):
    if(wikipedia_trending is not None):
        return
    else:
        return

# Build a dictionary with the matches between each combination of the three sources using the above functions
def get_all_matches(google_trending, twitter_trending, wikipedia_trending):
    matches = {}
    main_match = lexical_matching(twitter_trending, google_trending)
    matches['google-twitter'] = main_match
    matches['google-wikipedia'] = lexical_matching(google_trending, wikipedia_trending)
    matches['twitter-wikipedia'] = lexical_matching(twitter_trending, wikipedia_trending)
    matches['google-twitter-wikipedia'] = lexical_matching(main_match, wikipedia_trending)
    return matches