# Matching criteria, always keep the original elements of the first list in input which match the second list

import difflib
import re
import tagme
from fuzzywuzzy import fuzz
from sematch.semantic.similarity import WordNetSimilarity
from searsen_credentials import tagme_token

tagme.GCUBE_TOKEN = tagme_token

# Process the trends to be easily comparable, keeping the original strings
def text_processing(trend_list, keep_spaces = False):
    processed_list = []
    if(not isinstance(trend_list, list)): return []
    for trend in trend_list:
        processed_trend = {}
        processed_trend['original'] = trend
        trend = re.sub(' +', ' ', trend) # Remove multiple spaces (redundant, but useful to keep the single spaces if needed)
        # Keep the spaces in the smartest way possible
        if(keep_spaces == True): 
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

    if(len(matches) == 0): return 'No matches'
    return matches

# Compare two lists of trends using an euristic, also accepting partial matches
def syntactic_matching(trend_one, trend_two):
    trend_one_processed = text_processing(trend_one)
    trend_two_processed = text_processing(trend_two)
    matches = list({x['original'] for x in trend_one_processed for y in trend_two_processed if x['processed'] in y['processed'] or y['processed'] in x['processed']})
    
    if(len(matches) == 0): return 'No matches'
    return matches

# Compare two lists of trends using the fuzzy distances
def fuzzy_matching(trend_one, trend_two):
    matches = []
    trend_one_processed = text_processing(trend_one, keep_spaces = True)
    trend_two_processed = text_processing(trend_two, keep_spaces = True)
    for keyword_one in trend_one_processed:
        for keyword_two in trend_two_processed:
            if(fuzz.ratio(keyword_one['processed'], keyword_two['processed']) > 90 or 
            fuzz.partial_ratio(keyword_one['processed'], keyword_two['processed']) > 90 or
            fuzz.token_sort_ratio(keyword_one['processed'], keyword_two['processed']) > 90):
                matches.append(keyword_one['original'])

    if(len(matches) == 0): return 'No matches'
    return list(set(matches))

# Compare two lists of trends using the difflib library (no text processing required)
def sequence_matching(trend_one, trend_two):
    if(not isinstance(trend_one, list) or not isinstance(trend_two, list)): return 'No matches'
    threshold = 0.5
    matches = list({x for x in trend_one for y in trend_two if difflib.SequenceMatcher(None, x, y).ratio() > threshold})
    
    if(len(matches) == 0): return 'No matches'
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
    
    if(len(matches) == 0): return 'No matches'
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
            if(relations.relatedness[0].rel and int(relations.relatedness[0].rel) > 0): matches.append(keyword_one['original'])

    if(len(matches) == 0): return 'No matches'
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

    if(len(matches) == 0): return 'No matches'
    return matches

# Build a dictionary with the matches between each combination of the three sources using the above functions
def get_all_matches(google_trending, twitter_trending, wikipedia_trending):
    matches = {}
    # Syntactic matching seems to be the best for a list of keywords and hashtags
    main_match = syntactic_matching(twitter_trending, google_trending)
    matches['twitter-google'] = main_match
    matches['google-wikipedia'] = syntactic_matching(google_trending, wikipedia_trending)
    matches['twitter-wikipedia'] = syntactic_matching(twitter_trending, wikipedia_trending)
    matches['google-twitter-wikipedia'] = syntactic_matching(main_match, wikipedia_trending)
    return matches

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
    return performance_percentage

# Avoid to run the script when imported
if __name__ == '__main__':
    # Quick test with two lists containing every possible difficulty
    
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
 
    print('\nSemantic Matching:')
    semantic = semantic_matching(list_one, list_two)
    percent_semantic = compute_metrics(semantic, matches)
    
    #print('\nTagme matching:')
    #tagme = tagme_matching(list_one, list_two)
    #percent_tagme = compute_metrics(tagme, matches)
    
    print('\nNaive Matching:')
    naive = naive_matching(list_one, list_two)
    percent_naive = compute_metrics(naive, matches)
    
    print('\nSequence Matching:')
    sequence = sequence_matching(list_one, list_two)
    percent_sequence = compute_metrics(sequence, matches)

    print('\nSyntactic Matching:')
    syntactic = syntactic_matching(list_one, list_two)
    percent_syntactic = compute_metrics(syntactic, matches)
    
    print('\nFuzzy Matching:')
    fuzzy = fuzzy_matching(list_one, list_two)
    percent_fuzzy = compute_metrics(fuzzy, matches)
    
    print('\nHybrid Matching:')
    hybrid = hybrid_matching(list_one, list_two)
    percent_hybrid = compute_metrics(hybrid, matches)
    
    print('\nNUMBER OF MATCHINGS FOR THE TEST LISTS: ' + str(len(matches)) + '\n')