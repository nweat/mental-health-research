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

tweets = read.csv("D:\\twitter-mental-health-research\\mental-health-research\\patient_tweet_analysis\\bipolar\\bipolar_tweets.csv", header = TRUE)
tweets$tweetCreated <- ymd_hms(tweets$tweetCreated)
tweets$tweetCreated <- with_tz(tweets$tweetCreated, "America/New_York")
tweets$clean_text <- str_replace_all(tweets$tweetText, "@\\w+", "") # remove mentions
Sentiment <- get_nrc_sentiment(tweets$clean_text)
alltweets_senti <- cbind(tweets, Sentiment)

#alltweets_senti <- alltweets_senti %>% group_by(username,tweetCreated) %>% summarise(
#  anticipation = sum(anticipation),
#  disgust = sum(disgust),
#  fear = sum(fear),
#  joy = sum(joy),
#  sadness = sum(sadness),
#  surprise = sum(surprise),
#  trust = sum(trust),
#  negative = sum(negative),
#  positive = sum(positive),
#  anger = mean(anger)
#  )

#alltweets_senti

sentimentTotals <- data.frame(colSums(alltweets_senti[,c(11:20)]))
names(sentimentTotals) <- "count"
sentimentTotals <- cbind("sentiment" = rownames(sentimentTotals), sentimentTotals)
rownames(sentimentTotals) <- NULL

p1 = ggplot(data = sentimentTotals, aes(x = sentiment, y = count)) +
  geom_bar(aes(fill = sentiment), stat = "identity") +
  theme(legend.position = "none") +
  xlab("Sentiment") + ylab("Total Count") + ggtitle("Total Sentiment Score for All Tweets")

posnegtime <- alltweets_senti %>% 
  group_by(tweetCreated = cut(tweetCreated, breaks="2 days")) %>%
  summarise(negative = mean(negative),
            positive = mean(positive)) %>% melt

names(posnegtime) <- c("timestamp", "sentiment", "meanvalue")
posnegtime$sentiment = factor(posnegtime$sentiment,levels(posnegtime$sentiment)[c(2,1)])


p2 = ggplot(data = posnegtime, aes(x = as.Date(timestamp), y = meanvalue, group = sentiment)) +
  geom_line(size = 1.5, alpha = 0.7, aes(color = sentiment)) +
  geom_point(size = 0.3) +
  ylim(0, NA) + 
  scale_colour_manual(values = c("springgreen4", "firebrick3")) +
  theme(legend.title=element_blank(), axis.title.x = element_blank()) +
  scale_x_date(breaks = date_breaks("3 months"), 
               labels = date_format("%Y-%b")) +
  ylab("Average sentiment score") + 
  ggtitle("Sentiment Over Time")


alltweets_senti$month <- month(alltweets_senti$tweetCreated, label = TRUE)
monthlysentiment <- alltweets_senti %>% group_by(month) %>% 
  summarise(anger = mean(anger), 
            anticipation = mean(anticipation), 
            disgust = mean(disgust), 
            fear = mean(fear), 
            joy = mean(joy), 
            sadness = mean(sadness), 
            surprise = mean(surprise), 
            trust = mean(trust)) %>% melt

names(monthlysentiment) <- c("month", "sentiment", "meanvalue")

p3 = ggplot(data = monthlysentiment, aes(x = month, y = meanvalue, group = sentiment)) +
  geom_line(size = 2.5, alpha = 0.7, aes(color = sentiment)) +
  geom_point(size = 0.5) +
  ylim(0, NA) +
  theme(legend.title=element_blank(), axis.title.x = element_blank()) +
  ylab("Average sentiment score") + 
  ggtitle("Sentiment During the Year")

grid.newpage()
pushViewport(viewport(layout = grid.layout(2,2)))
vplayout <- function(x, y) viewport(layout.pos.row = x, layout.pos.col = y)
print(p1, vp = vplayout(1, 1:2))  # key is to define vplayout
print(p2, vp = vplayout(2, 1:2))  # key is to define vplayout
#print(p2, vp = vplayout(2, 1:2))  # key is to define vplayoutprint(p3, vp = vplayout(2, 2))  # key is to define vplayout
