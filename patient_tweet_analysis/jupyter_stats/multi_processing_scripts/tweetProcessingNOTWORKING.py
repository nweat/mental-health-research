import multiprocessing as mp
import pandas as pd
import pandas.util.testing as pdt
import numpy as np
from itertools import repeat
import preprocessor as pr
import re
from pattern.text.en import singularize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.lancaster import LancasterStemmer
import nltk
import sys
from unidecode import unidecode
##################################################################################
# PREPROCESS EVERY TWEET BEFORE FINAL DATA PREPARATION
# DESCRIPTION:
# Remove URL, mentions, RT word, 
# REFERENCES:
# http://www.clips.ua.ac.be/pages/pattern-en#ngram
# POSSIBLE FIXES:
# Spelling errors
# Fix stemming e.g. jesu should be jesus
# Replace emojis and smileys with word emotion
# To speed up: http://stackoverflow.com/questions/26784164/pandas-multiprocessing-apply
###################################################################################
#EMOJI_LIST = pd.read_csv('../emoji_table.csv') 
#STOP = stopwords.words('english')

html = r'<[^>]+>' # HTML tags
mentions = r'(?:@[\w_]+)' # @-mentions
url = r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+' # URLs
numbers = r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
rt = ('rt @')
hashtags = r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)" # hash-tags but only remove # and leave word, could add more meaning
letters_only = "[^a-zA-Z]"

words_with_dash_quotes = r"(?:[a-z][a-z'\-_]+[a-z])" # words with - and '
other_words = r'(?:[\w_]+)' # other words
anything_else = r'(?:\S)' # anything else
stop = stopwords.words('english')


def calcMoodStates(mood_lexicon, sentimentLabelledTweets):
    SAD_VALUES = []
    INSPIRED_VALUES = []
    HAPPY_VALUES = []
    DONT_CARE_VALUES = []
    ANNOYED_VALUES = []
    ANGRY_VALUES = []
    AMUSED_VALUES = []
    AFRAID_VALUES = []
    FOUND_WORDS = 0
    for token in sentimentLabelledTweets['stopWordsRemoved']:
        found = mood_lexicon.loc[mood_lexicon['Lemma'] == token]
        if len(found.index) > 1: 
            #found = found.iloc[1:2] #select the second by default
            if token in sentimentLabelledTweets['nouns']:
                found = found.loc[found['POS'] == 'n']
                
            FOUND_WORDS += 1
        elif len(found.index) == 1: 
            found = found.iloc[0:1]
            FOUND_WORDS +=1 
        if any(found['SAD'] >= threshold): SAD_VALUES.append(found['SAD'].round(2).values[0]) 
        if any(found['INSPIRED'] >= threshold): INSPIRED_VALUES.append(found['INSPIRED'].round(2).values[0]) 
        if any(found['HAPPY'] >= threshold): HAPPY_VALUES.append(found['HAPPY'].round(2).values[0])
        if any(found['DONT_CARE'] >= threshold): DONT_CARE_VALUES.append(found['DONT_CARE'].round(2).values[0])
        if any(found['ANNOYED'] >= threshold): ANNOYED_VALUES.append(found['ANNOYED'].round(2).values[0])
        if any(found['ANGRY'] >= threshold): ANGRY_VALUES.append(found['ANGRY'].round(2).values[0]) 
        if any(found['AMUSED'] >= threshold): AMUSED_VALUES.append(found['AMUSED'].round(2).values[0]) 
        if any(found['AFRAID'] >= threshold): AFRAID_VALUES.append(found['AFRAID'].round(2).values[0]) 
    sentimentLabelledTweets['SAD'] = np.mean(SAD_VALUES).round(2)
    sentimentLabelledTweets['INSPIRED'] = np.mean(INSPIRED_VALUES).round(2)
    sentimentLabelledTweets['HAPPY'] = np.mean(HAPPY_VALUES).round(2)
    sentimentLabelledTweets['DONT_CARE'] = np.mean(DONT_CARE_VALUES).round(2)
    sentimentLabelledTweets['ANNOYED'] = np.mean(ANNOYED_VALUES).round(2)
    sentimentLabelledTweets['ANGRY'] = np.mean(ANGRY_VALUES).round(2)
    sentimentLabelledTweets['AMUSED'] = np.mean(AMUSED_VALUES).round(2)
    sentimentLabelledTweets['AFRAID'] = np.mean(AFRAID_VALUES).round(2)
    sentimentLabelledTweets['FOUND_WORDS'] = FOUND_WORDS
    return sentimentLabelledTweets

def preprocessTweet(bipolar_tweets):
    #pr.set_options(pr.OPT.SMILEY, pr.OPT.EMOJI, pr.OPT.NUMBER) #text = pr.clean(text)
    frame = bipolar_tweets.tweetText.to_frame()
    tweet = bipolar_tweets.tweetText.str.lower() #.str.split()
    preprocesed = bipolar_tweets.tweetText.str.lower().str.replace(url, ' ', case=False).str.replace(mentions, ' ', case=False).str.strip()#.str.decode('utf-8')
    letters_Only = preprocesed.str.replace(letters_only, ' ', case=False).str.strip()

    data = tweet.replace(to_replace=stop, value="",regex=True)
    #tokenized = word_tokenize(frame['tweetText'].value)
    #bipolar_tweets['stop_words_remove'] = [w for w in tokenized if not w in stop]
    #str.replace(' ', '_')  str.replace(' ', '_')
    #text = unidecode(text.str.replace('"',''))
    #text = text.str.encode('unicode-escape').decode('utf-8')
    #textt = re.compile(r"(?:\@|https?\://)\S+").sub('', re.compile('rt @').sub('@', bipolar_tweets.tweetText.str).strip())
    # stops = set(stopwords.words("english")) 
    #bipolar_tweets['tweetText'] = text # replace tweet with cleaned version
    #tokenized = word_tokenize(str(text))

    #bipolar_tweets['tokenized'] = preprocesed.str.split() #';'.join(text)
    #bipolar_tweets['letters_only'] = bipolar_tweets.tweetText
    bipolar_tweets['stop_words_remove'] = bipolar_tweets.tweetText.values
    return bipolar_tweets

def process(bipolar_tweets):
    bipolar_tweets = bipolar_tweets.groupby('username').apply(preprocessTweet)
    return bipolar_tweets

if __name__ == '__main__':
    #print stop
    bipolar_tweets = pd.read_csv('../labelMIssingGeo_sentiment.csv', encoding = 'utf8')
    bipolar_tweets = bipolar_tweets.groupby('username')#.apply(preprocessTweet)
    bipolar_tweets['stop_words_remove'] = bipolar_tweets['tweetText'].apply(lambda x: [item for item in x if item not in stop])

    #p = mp.Pool(processes=8)
    #split_dfs = np.array_split(bipolar_tweets,8)
    #pool_results = p.map(process,split_dfs)    
    #p.close()
    #p.join()

    # merging parts processed by different processes
    #parts = pd.concat(pool_results)

    # merging newly calculated parts to big_df
    #big_df = pd.concat([big_df, parts], axis=1)
    bipolar_tweets.to_csv('../labelMIssingGeo_sentiment_pre.csv', index = False, encoding='utf-8')


    #preview = bipolar_tweets
    #print tabulate(preview, headers='keys', tablefmt='psql')
    #print tabulate([list(row) for row in preview.values], headers=list(preview.columns))

    # checking if the dfs were merged correctly
    #pdt.assert_series_equal(parts['id'], bipolar_tweets['id'])
