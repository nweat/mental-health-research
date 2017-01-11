#http://rpubs.com/cosmopolitanvan/r_isis_tweets_analytics
#http://stackoverflow.com/questions/25667453/lubridate-convert-date-time-to-a-formatted-time-string
#http://stackoverflow.com/questions/34838870/grid-arrange-from-gridextras-exiting-with-only-grobs-allowed-in-glist-afte/34839064
library(ggplot2)
library(lubridate)
library(scales)
library(tm)
library(stringr)
library(wordcloud)
library(syuzhet)
library(reshape2)
library(dplyr)
library(grid)
library(gridExtra)

tweets = read.csv("bipolar_patients_tweets.csv", header = TRUE)
tweets$tweetCreated <- ymd_hms(tweets$tweetCreated)
tweets$tweetCreated <- with_tz(tweets$tweetCreated, "America/New_York")
tweets$clean_text <- str_replace_all(tweets$tweetText, "@\\w+", "") # remove mentions
Sentiment <- get_nrc_sentiment(tweets$clean_text)
alltweets_senti <- cbind(tweets, Sentiment)

sentimentTotals <- data.frame(colSums(alltweets_senti[,c(11:18)]))
names(sentimentTotals) <- "count"
sentimentTotals <- cbind("sentiment" = rownames(sentimentTotals), sentimentTotals)
rownames(sentimentTotals) <- NULL

sentimentTotals

ggplot(data = sentimentTotals, aes(x = sentiment, y = count)) +
  geom_bar(aes(fill = sentiment), stat = "identity") +
  theme(legend.position = "none") +
  xlab("Sentiment") + ylab("Total Count") + ggtitle("Total Sentiment Score for All Tweets")




#grid.newpage()
#pushViewport(viewport(layout = grid.layout(3, 3)))
#vplayout <- function(x, y) viewport(layout.pos.row = x, layout.pos.col = y)
#print(p1, vp = vplayout(1, 3))  # key is to define vplayout


