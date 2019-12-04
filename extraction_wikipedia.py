# Wikipedia data extraction - using Pageviewapi

import pageviewapi
import os
from attrdict import AttrDict
import pandas as pd
from pandas.io.json import json_normalize

# Fetch the pageviews for a specific article
def fetch_timeseries_wikipedia(keyword, save_csv = True):
    try:
        interest_over_time = pageviewapi.per_article('it.wikipedia', keyword, '20151101', '20191101',
                                                     access='all-access', agent='all-agents', granularity='daily')
    except: 
        print('The chosen article doesn\'t exist')
        return None

    # Save in a csv if needed
    if(save_csv): 
        # Csv naming and path
        data_path = 'data/wikipedia/'
        if not os.path.exists(data_path): os.makedirs(data_path)
        file_name = data_path + keyword.lower() + '_wikipedia_interest.csv'
        interest_over_time_df = pd.DataFrame(interest_over_time)
        interest_over_time_df.to_csv(file_name, index=False, encoding='utf-8')

    return interest_over_time

# Get trending articles in Italy as an ordered list
def fetch_trending_wikipedia():
    # Returns an AttrDict
    trends_it = pageviewapi.top('it.wikipedia', 2019, 11, 14, access='all-access')
    trends_it_final = []
    for article in trends_it['items'][0]['articles']:
        trends_it_final.append(article['article'])
    
    return trends_it_final


# Avoid to run the script when imported
if __name__ == '__main__':
    # Variabled needed (tries to take it from user or use default)
    input_keyword = input('\nInsert a keyword (default: Donald_Trump) -> ')
    if(not input_keyword.strip()):
        keyword = 'Donald_Trump'
    else:
        keyword = input_keyword

    fetch_timeseries_wikipedia(keyword)

