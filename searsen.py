# Main file. Uses the extraction modules and their output to plot the time series and compare them

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from extraction_google import fetch_csv_google
from extraction_twitter import fetch_csv_twitter

data_path_google = 'data/google/'
data_path_twitter = 'data/twitter/'
files = os.listdir(data_path_google)
if(not files): sys.exit('The folder is empty')

print('Choose the desired file number')
for i in range(len(files)): print(str(i) + ' - ' + files[i])
chosen_file = input('-> ')
try: value = int(chosen_file)
except ValueError:
   print('Invalid argument, using the first listed file')
   value = 0
if(not files[value]): 
   print('Invalid argument, using the first listed file')
   value = 0 
file_path = data_path_google + files[value]
print(file_path)

# *** Test ***
#time_window = 'today 5-y'
#keywords = ['test']
#fetch_csv_google(keywords, time_window)

df = pd.read_csv(file_path, delim_whitespace=True, parse_dates=[0], infer_datetime_format=True)
plt.plot(df['date'], df['trump'], 'ro--')
plt.show()
# *** Test ***