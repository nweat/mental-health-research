import os, csv
import pandas as pd
from multiprocessing import Pool
import keyword_extraction_w_parser
from nltk.corpus import stopwords
import string
import re
from collections import Counter
from unicodedata import normalize
from nltk import bigrams 

###############################################################################################
#########################         KEYWORD EXTRACTION             #############################
###############################################################################################


emoticons_str = r"""
(?:
    [:=;] # Eyes
    [oO\-]? # Nose (optional)
    [D\)\]\(\]/\\OpP] # Mouth
)"""

regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]
    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
     
def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens


# wrap your csv importer in a function that can be mapped
def process_csv(filename):
    # https://marcobonzanini.com/2015/03/17/mining-twitter-data-with-python-part-3-term-frequencies/
    # https://github.com/naushadzaman/keyword-extraction-from-tweets
    # look at keyword extraction after, for now for each user get most frequent words/bigrams
    # also look at lemmatization/stemming
    # look at emoticons
    uniqueUsers = []

    punctuation = list(string.punctuation)
    stop = stopwords.words('english') + punctuation + ['rt', 'via']

    with open(filename, 'r') as readin:
        reader = csv.DictReader(readin, delimiter=',')
        rows = list(reader)
    
    # get unique twitter users
    for row in rows:
        if row['username'] not in uniqueUsers:
            uniqueUsers.append(row['username'])
 
    
    # for each unique user get frequent words from their tweets
    f = open('bipolar_comorbid_tweets_extracted_200common_words_per_user.csv', 'wb')
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(["username","freqwords","freqhashtags","freqmentions"])
    for usr in uniqueUsers:
        print usr
        count_all = Counter()
        count_hash = Counter()
        count_mentions = Counter()
        freqwords = []
        freqhashtags = []
        freqmentions = []
        for row in rows:
            if row['username'] == usr:
                #terms_all = [term for term in preprocess(row['tweetText'].lower().decode('unicode_escape').encode('ascii','ignore')) if term not in stop]
                terms_hash = [term for term in preprocess(row['tweetText'].lower()) if term.startswith('#')]
                terms_mentions = [term for term in preprocess(row['tweetText'].lower()) if term.startswith('@')]
                terms_only = [term for term in preprocess(row['tweetText'].lower()) if term not in stop and not term.startswith(('#', '@'))] #.decode('unicode_escape').encode('ascii','ignore')
                terms_only = set(terms_only)
                terms_hash = set(terms_hash)
                terms_mentions = set(terms_mentions)
                #terms_bigram = bigrams(terms_all)
                count_all.update(terms_only)
                count_hash.update(terms_hash)
                count_mentions.update(terms_mentions)

        for word, count in count_all.most_common(200):
            freqwords.append(word)
        for word, count in count_hash.most_common(200):
            freqhashtags.append(word)
        for word, count in count_mentions.most_common(200):
            freqmentions.append(word)

        writer.writerow([usr, " ".join(freqwords), " ".join(freqhashtags), " ".join(freqmentions)]) 

def main():
    # set up your pool
    pool = Pool(processes = 8) # or whatever your hardware can support

    # get a list of file names
    #files = os.listdir('.')
    file_list = ['bipolar_comorbid/bipolar_comorbid_tweets.csv']

    #for f in file_list:
      # process_csv(f)

    # have your pool map the file names to dataframes
    df_list = pool.map(process_csv, file_list)

    # reduce the list of dataframes to a single dataframe
   # combined_df = pd.concat(df_list, ignore_index=True)

if __name__ == '__main__':
    main()