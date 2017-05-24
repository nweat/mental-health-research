import multiprocessing as mp
import pandas as pd
import pandas.util.testing as pdt
import numpy as np
import csv
from itertools import repeat

##################################################################################
# CALCULATE AND LABEL MOOD STATES OF EACH PATIENTS TWEETS BASED ON DEPECHE MOOD LEXICON
# DESCRIPTION:
# For each tweet, tokenize, group all scores for each mood where weighting is over 15%
# FIXES:
# Select which tense of the word based on POS tag to choose bcas the lexicon has multiple e.g. will#v will#n, currently choosing verb
# REFERENCES:
# http://stackoverflow.com/questions/30787901/how-to-get-a-value-from-a-pandas-dataframe-and-not-the-index-and-object-type
###################################################################################

def labelMissingGeoTag(bipolar_tweets, user_top_used_geo_tag):
    found = user_top_used_geo_tag.loc[user_top_used_geo_tag['username'] == bipolar_tweets['username'].iloc[0]]
    bipolar_tweets.tweetLat.fillna(found['tweetLat'].values[0], inplace=True)
    bipolar_tweets.tweetLong.fillna(found['tweetLong'].values[0], inplace=True)
    return bipolar_tweets

def process((bipolar_tweets, user_top_used_geo_tag)):
    bipolar_tweets_with_geo = bipolar_tweets.groupby('username').apply(labelMissingGeoTag, user_top_used_geo_tag)
    return bipolar_tweets_with_geo

if __name__ == '__main__':
    bipolar_tweets = pd.read_csv('../initial_data/selected_normal_users_tweets_less5.csv')

    df = bipolar_tweets.groupby(['username', 'tweetLat','tweetLong'])['tweetLong'].agg({'count':'count'})
    mask = df.groupby(level=0).agg('idxmax')
    user_top_used_geo_tag = df.loc[mask['count']]
    user_top_used_geo_tag = user_top_used_geo_tag.reset_index()

    p = mp.Pool(processes=8)
    split_dfs = np.array_split(bipolar_tweets,8)
    pool_results = p.map(process,zip(split_dfs,repeat(user_top_used_geo_tag)))     
    p.close()
    p.join()

    # merging parts processed by different processes
    parts = pd.concat(pool_results)

    # merging newly calculated parts to big_df
    #big_df = pd.concat([big_df, parts], axis=1)
    parts.to_csv('../final_data/users_final_normal/labelMIssingGeo_normalusers.csv', index = False, quotechar='"', quoting=csv.QUOTE_ALL) #, encoding='utf-8'

    # checking if the dfs were merged correctly
    #pdt.assert_series_equal(parts['id'], bipolar_tweets['id'])
