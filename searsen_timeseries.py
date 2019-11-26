# Main file for timeseries. Uses the extraction modules and their output to plot the time series and compare them

import os
import sys
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# Take a csv, plot and analyze
def analyze_data():
    data_path_google = 'data/google/'
    data_path_twitter = 'data/twitter/'
    data_path = input('''
Choose the data folder (default: 1)
1 - Google
2 - Twitter
-> ''')
    if(data_path == '1'): chosen_data_path = data_path_google
    elif(data_path == '2'): chosen_data_path = data_path_twitter
    else: chosen_data_path = data_path_google

    files = os.listdir(chosen_data_path)
    if(not files): sys.exit('\nThe selected data folder is empty')

    print('\nChoose the desired file number')
    for i in range(len(files)): print(str(i) + ' - ' + files[i])
    chosen_file = input('-> ')
    try: value = int(chosen_file)
    except ValueError:
        print('\nInvalid argument, using the first listed file')
        value = 0
    if(not files[value]): 
        print('\nInvalid argument, using the first listed file')
        value = 0 
    file_path = data_path_google + files[value]

    # Plot the selected csv
    plot_path = 'plots/'
    if not os.path.exists(plot_path): os.mkdir(plot_path)
    plot_name = files[value][:-4] + '_plot.png'
    df = pd.read_csv(file_path, parse_dates=[0], infer_datetime_format=True, sep=';')
    plt.plot(df.iloc[:,0], df.iloc[:,1], 'ro--')
    print('\nPreparing the plot...')
    plt.savefig(plot_path + plot_name, dpi = 300)
    print('\nPlot saved in plots/ folder\n')
    plt.show()


# Main part of Searsen, to guide the user through the entire process
extraction_pref = input('''
*************** SEARSEN ***************
Extract and compare searches and sentiment

Do you want to extract data? (default: 3)
1 - Extract from Google
2 - Extract from Twitter
3 - Skip extraction
-> ''')
if(extraction_pref == '1'): 
    subprocess.call('python extraction_google.py', shell=True)
    analyze_data()
elif(extraction_pref == '2'): 
    subprocess.call('python extraction_twitter.py', shell=True)
    analyze_data()
elif(extraction_pref == '3'): 
    analyze_data()
else: 
    print('\nInvalid argument, using default')
    analyze_data()