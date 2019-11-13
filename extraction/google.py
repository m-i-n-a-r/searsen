# Google data extraction - use Google Trends to save the daily searches of one or more keywords

from pytrends.request import TrendReq

# Variabled needed (tries to take it from user or use a default array)
separator = ','
data_path = 'data/google/'
input_keywords = input('Insert an array of comma separated keywords: ')
if(not input_keywords.strip()): keywords = ['trump', 'clinton']
else: keywords = input_keywords.split(separator)
file_name = data_path + '_'.join(keywords).replace(' ', '') + '_interest_over_time.csv'


# Login to Google. Only need to run this once, the rest of requests will use the same session.
pytrend = TrendReq()
# Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
pytrend.build_payload(kw_list=keywords)

# Interest Over Time
interest_over_time_df = pytrend.interest_over_time()
print(interest_over_time_df)
print('')
interest_over_time_df.to_csv(file_name, sep=';', encoding='utf-8')

# Related Queries, returns a dictionary of dataframes
related_queries_dict = pytrend.related_queries()
print(related_queries_dict)
print('')

# Get Google Keyword Suggestions
suggestions_dict = pytrend.suggestions(keyword=keywords[0])
print(suggestions_dict)
print('')

# Get Google Hot Trends data
#trending_searches_df = pytrend.trending_searches()
#print(trending_searches_df.head())

# Get Google Today Hot Trends data
#today_searches_df = pytrend.today_searches()
#print(today_searches_df.head())

# Get Google Top Charts
#top_charts_df = pytrend.top_charts(2018, hl='en-US', tz=300, geo='GLOBAL')
#print(top_charts_df.head())