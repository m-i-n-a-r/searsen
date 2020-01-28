# Provide some useful functions to analyze the dataset

from pymongo import MongoClient

# Given a keyword, check how many hours it was in the trends
def trend_lifecycle(trend):
    return

# Compare two set of trends shifting them in time (eg Twitter trends at 7 AM vs Google trends at 9 AM)
def trend_shifted_comparison():
    return

# Estimate the polarization for a selected keyword
def estimate_polarization():
    return

# Main part of the script, use the above functions to compute results
client = MongoClient('mongodb://127.0.0.1:27017')