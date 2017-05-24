import os, csv
import pandas as pd
from multiprocessing import Pool
import keyword_extraction_w_parser
import string
from nltk.corpus import stopwords
import re
from collections import Counter
from unicodedata import normalize
from unidecode import unidecode
from nltk import bigrams 


###############################################################################################
#########################         KEYWORD EXTRACTION             #############################
###############################################################################################

normal_users = 'jupyter_stats/final_data/users_final_normal/'
bipolar_users = 'jupyter_stats/final_data/users_final/'
file_in_normal = normal_users + 'labelMIssingGeo_normalusers.csv'
file_out_normal = normal_users + 'normal_user_extracted_400_common_words_per_user.csv'
file_in_bipolar = bipolar_users + 'labelMIssingGeo_preprocessed.csv'
file_out_bipolar = bipolar_users + 'bipolar_user_extracted_400_common_words_per_user.csv'

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
    f = open(file_out_normal, 'wb')
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(["username","freqwords","freqhashtags","freqmentions"])
    for usr in uniqueUsers:
        print usr
        count_all = Counter()
        count_hash = Counter()
        count_mentions = Counter()
        count_bigrams = Counter()
        freqwords = []
        freqhashtags = []
        freqmentions = []
        freqbigrams = []
        for row in rows:
            if row['username'] == usr:
                text = row['tweetText'].lower() #" ".join(row['withStopWords']).strip() #row['tweetText']
                hashtags = row['hashtags']
                mentions = row['mentions']
                #terms_all = [term for term in preprocess(row['tweetText'].lower().decode('unicode_escape').encode('ascii','ignore')) if term not in stop]
                terms_hash = [term for term in preprocess(unidecode(hashtags)) if term.startswith('#')]
                terms_mentions = [term for term in preprocess(unidecode(mentions)) if term.startswith('@')]
                terms_only = [term for term in preprocess(unidecode(text)) if term not in stop and not term.startswith(('#', '@'))] #.decode('unicode_escape').encode('ascii','ignore')
                terms_bigram = [term for term in preprocess(unidecode(text)) if term not in stop]
                terms_only = set(terms_only)
                terms_hash = set(terms_hash)
                terms_mentions = set(terms_mentions)
                #terms_bigram = bigrams(terms_bigram)
                #terms_bigram = set(terms_bigram)
                #terms_bigram = bigrams(terms_all)
                count_all.update(terms_only)
                count_hash.update(terms_hash)
                count_mentions.update(terms_mentions)
                #count_bigrams.update(terms_bigram)


        for word, count in count_all.most_common():
            freqwords.append(word)
        for word, count in count_hash.most_common():
            freqhashtags.append(word)
        for word, count in count_mentions.most_common():
            freqmentions.append(word)
        #for word, count in count_bigrams.most_common():
            #freqbigrams.append(word)


        writer.writerow([(usr), " ".join((freqwords)), " ".join((freqhashtags)), " ".join((freqmentions))])  #, " ".join(str(freqbigrams))

def main():
    # set up your pool
    pool = Pool(processes = 8) # or whatever your hardware can support

    # get a list of file names
    #files = os.listdir('.')
    
    file_list = [file_in_normal]

    #for f in file_list:
      # process_csv(f)

    # have your pool map the file names to dataframes
    df_list = pool.map(process_csv, file_list)

    # reduce the list of dataframes to a single dataframe
   # combined_df = pd.concat(df_list, ignore_index=True)

if __name__ == '__main__':
    main()