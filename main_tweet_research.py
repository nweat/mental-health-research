__author__ = 'nweat'

try:
	import json
except ImportError:
	import simplejson as json

import research_scripts,sys,time,getopt,codecs
# Import the necessary methods from "twitter" library
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

def main(argv):
	ifile = ''
	ofile = ''
	processed_diagnosed_users = []

	#setup twitter connection
	ACCESS_TOKEN = '3078842881-mmB75oipEz6AO4nmbOTcaOpYAAlWbDj2TFLB3xk'
	ACCESS_SECRET = '0pwoDFiRSQE4tpT3B7itCTdUT35pqtvUp35jN6XHBSefj'
	CONSUMER_KEY = '6mLYYFesfAjHWVroH4advv1xb'
	CONSUMER_SECRET = 'lBeFRdW3d61IvCNzoxLkEu8jHa3V1xojQowfnhQsnIrLxCQekp'
	oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
	twitter = Twitter(auth=oauth)

	if len(argv) == 0:
		print 'You must pass some parameters'
		return

	try:
		r = research_scripts.oldtweets_scripts.TweetResearch()
		opts, args = getopt.getopt(argv, "", ("ifile=","ofile="))
				
		for opt,arg in opts:
			if opt == '--ifile':
				ifile = arg
			elif opt == '--ofile':
				ofile = arg

		inputFile = codecs.open(ifile, 'r', encoding="utf-8")
		outputFile = codecs.open(ofile, "w+", "utf-8")
		outputFile.write('screenName;created;location;geoEnabled;description;diagnosisMade;diagnosisStatement;NumTweetsYrUpToDiagnosis;NumTweetsPosted;Retweets;numFavorites;numFollowers;numFriends;AdvocateRefDesc;DiseaseRefDiagnosis;DepressionRefDesc;DepressionRefDiagnosis;SurvivorRefDesc')
		
		print "\n******Extracting twitter users who made depression diagnosis statements from Oct-20-2014-Oct-20-2016******"
		diagnosed_users = r.extractDiagnosedUsers(inputFile)
		if diagnosed_users:
			print "Done..."

		print "\n******Generating stats for twitter users who made depression diagnosis statements from Oct-20-2014-Oct-20-2016******"
		processed_diagnosed_users = r.process(diagnosed_users, outputFile, twitter)
		outputFile.flush()
		
	except arg:
		print 'Arguments parser error ' + arg
	finally:
		inputFile.close()
		outputFile.close()
		#print '\n%s Results added to file\n' % processed_diagnosed_users


if __name__ == '__main__':
	main(sys.argv[1:]) #1: refers to parameters needed to be supplied