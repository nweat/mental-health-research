#STARTING: https://rstudio-pubs-static.s3.amazonaws.com/132792_864e3813b0ec47cb95c7e1e2e2ad83e7.html
#http://rpubs.com/cosmopolitanvan/r_isis_tweets_analytics
#https://georeferenced.wordpress.com/2013/01/15/rwordcloud/
#https://rstudio-pubs-static.s3.amazonaws.com/31867_8236987cf0a8444e962ccd2aec46d9c3.html
#http://stackoverflow.com/questions/18153504/removing-non-english-text-from-corpus-in-r-using-tm
#http://stackoverflow.com/questions/31702488/text-mining-with-tm-package-in-r-remove-words-starting-from-http-or-any-other

# remove mentions and hashtags and URLs for now and special characters
# do seperate cloud for hashtags
# distribution of tweets by user, 

library(tm)
library(SnowballC)
library(wordcloud)
library(rjson)
library(stringr)
library(grid)
library(gridExtra)

#custom tweet cleaning
#removeURL <- function(x) gsub("http[[:alnum:]]*", "", x)

tweets = read.csv("D:\\twitter-mental-health-research\\mental-health-research\\patient_tweet_analysis\\depression\\depression_tweets_extracted_200common_words_per_user.csv", header = TRUE)
#tweets = fromJSON(file = "bipolar_comorbid_patient_tweets.json" )
review_corpus = Corpus(VectorSource(tweets$freqhashtags)) #readerControl = list(blank.lines.skip=TRUE
review_corpus = tm_map(review_corpus, PlainTextDocument)   
review_corpus = tm_map(review_corpus, content_transformer(tolower))
#review_corpus = tm_map(review_corpus, removeURL)
#review_corpus = tm_map(review_corpus, removeNumbers)
review_corpus = tm_map(review_corpus, removePunctuation)
review_corpus = tm_map(review_corpus, removeWords, c('the','make','year','tweet', 'this', 'use', 'guy', 'girl','ive','get','dont','say', stopwords("english")))
review_corpus = tm_map(review_corpus, stemDocument)   
review_corpus = tm_map(review_corpus, stripWhitespace)

#inspect(review_corpus[1])
#dataframe = data.frame(text=unlist(sapply(review_corpus, `[`, "content")), stringsAsFactors=F)
#dataframe
review_dtm_tfidf = DocumentTermMatrix(review_corpus, control = list(weighting = weightTfIdf))
review_dtm_tfidf = removeSparseTerms(review_dtm_tfidf, 0.95) # remove less frequent words
review_dtm_tfidf
freq = data.frame(sort(colSums(as.matrix(review_dtm_tfidf)), decreasing=TRUE)) 
wordcloud(rownames(freq), freq[,1], random.order = FALSE, colors=brewer.pal(1, "Dark2"))# max.words=100, #random.order = FALSE



#Frequency
review_dtm_freq = DocumentTermMatrix(review_corpus)
review_dtm_freq = removeSparseTerms(review_dtm_freq, 0.95) 
freq2 = data.frame(sort(colSums(as.matrix(review_dtm_freq)), decreasing=TRUE))
#wordcloud(rownames(freq2), freq2[,1], random.order = FALSE, colors=brewer.pal(1, "Dark2")) #max.words=100,


#to generate:
#frequency_patients_description.png
#tfidf_patient_description.png #with sparse terms
#tfidf_patients_description_less0.95_sparsity_setting.png #without sparse terms

