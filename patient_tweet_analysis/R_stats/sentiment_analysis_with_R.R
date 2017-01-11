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

#SAMPLE TWEET CREATED DATE FORMAT:: 2016-12-28 05:38:01
tweets = read.csv("bipolar_patients_tweets.csv", header = TRUE)
tweets$tweetCreated = ymd_hms(tweets$tweetCreated)
tweets$tweetCreated = with_tz(tweets$tweetCreated, "America/New_York")


#TWEETS DATE ANALYSIS: Which days, month, time of day tweet more?

p1 = ggplot(data = tweets, aes(x = month(tweetCreated, label = TRUE))) +
  geom_bar(aes(fill = ..count..)) +
  theme(legend.position = "none") +
  xlab("Month") + ylab("Number of tweets") +
  scale_fill_gradient(low = "midnightblue", high = "aquamarine4")

p2 = ggplot(data = tweets, aes(x = wday(tweetCreated, label = TRUE))) +
  geom_bar(aes(fill = ..count..)) +
  theme(legend.position = "none") +
  xlab("Day of the Week") + ylab("Number of tweets") + 
  scale_fill_gradient(low = "midnightblue", high = "aquamarine4")

tweets$timeonly = as.numeric(tweets$tweetCreated - trunc(tweets$tweetCreated, "days"))
class(tweets$timeonly) <- "POSIXct"

p3 = ggplot(data = tweets, aes(x = timeonly)) +
  geom_histogram(aes(fill = ..count..)) +
  theme(legend.position = "none") +
  xlab("Time") + ylab("Number of tweets") + 
  scale_x_datetime(breaks = date_breaks("2 hours"), 
                   labels = date_format("%H:00")) +
  scale_fill_gradient(low = "midnightblue", high = "aquamarine4")

grid.newpage()
pushViewport(viewport(layout = grid.layout(3, 1)))
vplayout <- function(x, y) viewport(layout.pos.row = x, layout.pos.col = y)
print(p1, vp = vplayout(1, 1))  # key is to define vplayout
print(p2, vp = vplayout(2, 1))
print(p3, vp = vplayout(3, 1))

