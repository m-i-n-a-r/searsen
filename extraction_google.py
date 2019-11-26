# Google data extraction - use Google Trends to save the daily searches of one or more keywords

import os
from pytrends.request import TrendReq
from pytrends import dailydata

# Fetch the use of a set of keywords in a specified time window
def fetch_timeseries_google(keywords, time_window):
    # Csv name
    data_path = 'data/google/'
    if not os.path.exists(data_path): os.makedirs(data_path)
    file_name = data_path + '_'.join(keywords).replace(' ', '') + '_google_interest.csv'

    # Login to Google. Only need to run this once, the rest of requests will use the same session.
    pytrend = TrendReq()
    # Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
    pytrend.build_payload(kw_list=keywords, timeframe=time_window)

    # Interest Over Time
    interest_over_time_df = pytrend.interest_over_time()
    interest_over_time_df.to_csv(file_name, sep=';', encoding='utf-8')

    # Related Queries, returns a dictionary of dataframes
    #related_queries_dict = pytrend.related_queries()
    # Get Google Keyword Suggestions
    #suggestions_dict = pytrend.suggestions(keyword=keywords[0])

# Get the Google hot queries
def fetch_trending_google():
    # Login to Google. Only need to run this once, the rest of requests will use the same session.
    pytrend = TrendReq()

    # Get Google Hot Trends data
    #trends_us = pytrend.trending_searches(pn='united_states')
    trends_it_df = pytrend.trending_searches(pn='italy')
    trends_it_final = trends_it_df.iloc[:,0].tolist()

    return trends_it_final


# Avoid to run the script when imported
if __name__ == '__main__':
    # Variabled needed (tries to take it from user or use default)
    separator = ','
    input_keywords = input('\nInsert an array of comma separated keywords (default: trump, clinton) -> ')
    if(not input_keywords.strip()): keywords = ['trump', 'clinton']
    else: keywords = input_keywords.split(separator)
    input_time_window = input(
    '''
Insert the time window (default: 2) 
1 - 2004 to today (monthly) 
2 - Last 5 years (weekly)
3 - Last 3 months (daily)
4 - Last week (hourly)
-> ''')
    if(input_time_window == '1'): time_window = 'all'
    elif(input_time_window == '2'): time_window = 'today 5-y'
    elif(input_time_window == '3'): time_window = 'today 3-m'
    elif(input_time_window == '4'): time_window = 'now 7-d'
    else: 
        print ('\nInvalid value, default set')
        time_window = 'today 5-y'

    fetch_timeseries_google(keywords, time_window)