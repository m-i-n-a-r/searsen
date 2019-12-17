# Matching criteria, to detect the eventual relation between two different keywords or to match similar or identical keywords

import difflib

# Compare two or three lists of trends using a simple list intersection
def intersection_matching(google_trending, twitter_trending, wikipedia_trending = None):
    processed_google = [trend.lower().replace(' ', '') for trend in google_trending]
    processed_twitter = [trend.lower().replace(' ', '') for trend in twitter_trending]
    if(wikipedia_trending is not None): 
        processed_wikipedia = [trend.lower().replace('_', '') for trend in wikipedia_trending]
        matching_trends_all = list(set(processed_google) & set(processed_twitter) & set(processed_wikipedia))
    else:
        matching_trends_all = list(set(processed_google) & set(processed_twitter))

    return matching_trends_all

# Compare two or three lists of trends accepting also partial matchings
def advanced_matching(google_trending, twitter_trending, wikipedia_trending = None):
    processed_google = [trend.lower().replace(' ', '').replace('-', '') for trend in google_trending]
    processed_twitter = [trend.lower().replace(' ', '').replace('-', '') for trend in twitter_trending]
    if(wikipedia_trending is not None):
        processed_wikipedia = [trend.lower().replace('_', '').replace('-', '') for trend in wikipedia_trending]
        matching_trends_first = list({twitter_trending[processed_twitter.index(y)] for x in processed_google for y in processed_twitter if x in y or y in x})
        matching_trends = list({x for x in matching_trends_first for y in processed_wikipedia if x.lower().replace(' ', '').replace('-', '') in y or y in x.lower().replace(' ', '').replace('-', '')})
    else:
        matching_trends = list({twitter_trending[processed_twitter.index(y)] for x in processed_google for y in processed_twitter if x in y or y in x})
    
    return matching_trends

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
def semantic_matching(google_trending, twitter_trending, wikipedia_trending = None):   
    if(wikipedia_trending is not None):
        return
    else:
        return

# Compare two or three lists of trends using all the above approaches TODO
def hybrid_matching(google_trending, twitter_trending, wikipedia_trending = None):
    if(wikipedia_trending is not None):
        return
    else:
        return
    return