# Wikipedia data extraction - using Pageviewapi

import pageviewapi
import os
import datetime
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

# Get trending articles in Italy as an ordered list, cut them if necessary (updated daily)
def fetch_trending_wikipedia(cut = 0):
    # Get the current date to select yesterday's trending articles (month and day must have the leading zero)
    special_pages = ['Speciale:Ricerca', 'Pagina_principale', 'Speciale:UltimeModifiche', 'Special:Search']
    now = datetime.datetime.now() - datetime.timedelta(days=1)
    year = now.year
    month = f"{now.month:02d}"
    day = f"{now.day:02d}"
    # Returns an AttrDict
    trends_it = pageviewapi.top('it.wikipedia', year, month, day, access='all-access')
    trends_it_final = []
    counter = 0
    for article in trends_it['items'][0]['articles']:
        if(article['article'] in special_pages): continue
        else: 
            trends_it_final.append(article['article'])
            counter += 1
            if(counter == cut + 1): break
    
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

