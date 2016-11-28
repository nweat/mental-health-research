__author__ = 'nweat'

try:
	import json
except ImportError:
	import simplejson as json

import data_manager,sys,time,getopt,codecs
# Import the necessary methods from "twitter" library
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import tweepy
#http://superuser.com/questions/602587/how-to-use-latest-python-2-7-x-the-right-way-on-ubuntu-12-04-lts

def main(argv):
	ifile = ''
	ofile = ''
	stats = ''
	normalusers = ''
	illness = ''
	processed_diagnosed_users = []

	#setup twitter connection
	ACCESS_TOKEN = '3078842881-mmB75oipEz6AO4nmbOTcaOpYAAlWbDj2TFLB3xk'
	ACCESS_SECRET = '0pwoDFiRSQE4tpT3B7itCTdUT35pqtvUp35jN6XHBSefj'
	CONSUMER_KEY = '6mLYYFesfAjHWVroH4advv1xb'
	CONSUMER_SECRET = 'lBeFRdW3d61IvCNzoxLkEu8jHa3V1xojQowfnhQsnIrLxCQekp'
	#oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
	#twitter = Twitter(auth=oauth,retry=True)
	#twitter_stream = TwitterStream(auth=oauth)

	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
	api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	print api.home_timeline(count = 3)

	if len(argv) == 0:
		print 'You must pass some parameters'
		return

	try:
		obj = data_manager.manager.TweetManager(api, twitter_stream)
		opts, args = getopt.getopt(argv, "", ("ifile=","ofile=","stats=","illness=","normalusers="))
				
		for opt,arg in opts:
			if opt == '--ifile':
				ifile = arg
			elif opt == '--ofile':
				ofile = arg
			elif opt == '--stats':
				stats = arg
			elif opt == '--illness':
				illness = arg
			elif opt == '--normalusers':
				normalusers = arg

		inputFile = codecs.open(ifile, 'r', encoding = "utf-8")
		outputFile = codecs.open(ofile, "w+", "utf-8")

		if stats and illness:	
			#outputFile.write('screenName;created;location;geoEnabled;description;diagnosisMade;diagnosisStatement;NumTweetsYrUpToDiagnosis;NumTweetsPosted;Retweets;numFavorites;numFollowers;numFriends;AdvocateRefDesc;DiseaseRefDiagnosis;DepressionRefDesc;DepressionRefDiagnosis;SurvivorRefDesc')
			
			print "\n******Extracting twitter users who made diagnosis statements******"
			diagnosed_users = obj.extractDiagnosedUsers(inputFile)
			if diagnosed_users:
				print "Done..."

			print "\n******Generating stats for twitter users who made diagnosis statements******"
			#processed_diagnosed_users = obj.generate_stats(illness, diagnosed_users, twitter)
			#outputFile.write(json.dumps(processed_diagnosed_users, sort_keys = True, indent=4, ensure_ascii=False, separators=(',', ':')))
			
			#print processed_diagnosed_users
			#outputFile.flush()
		
	except arg:
		print 'Arguments parser error ' + arg
	finally:
		inputFile.close()
		outputFile.close()
		print '\n%s Results added to file\n' % len(processed_diagnosed_users)


if __name__ == '__main__':
	main(sys.argv[1:]) #1: refers to parameters needed to be supplied