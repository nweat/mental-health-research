__author__ = 'nweat'

try:
	import json
except ImportError:
	import simplejson as json

import data_manager,sys,time,getopt,codecs
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
	twitter = Twitter(auth=oauth,retry=True)
	twitter_stream = TwitterStream(auth=oauth)


	if len(argv) == 0:
		print 'You must pass some parameters'
		return

	try:
		r = data_manager.manager.TweetManager(twitter, twitter_stream)
		opts, args = getopt.getopt(argv, "", ("ifile=","ofile=","action="))
				
		for opt,arg in opts:
			if opt == '--ifile':
				ifile = arg
			elif opt == '--ofile':
				ofile = arg

		#outputFile = codecs.open(ofile, "w+", "utf-8")
		#diagnosed_users = r.extractDiagnosedUsers(inputFile)
		#_id = twitter.users.show(screen_name='nikkiweat_nikki')['id_str']
		#userIDs = r.get_all_followers_ids(_id) #set starting node
		#print userIDs
		#getUsers = twitter.users.lookup(user_id=','.join(map(str, userIDs)))
		#for usr in getUsers:
		#	print usr['screen_name']

		#random_seed = r.select_random_seed_node()
		#print random_seed
		#ids = r.breadth_traversal(random_seed, outputFile) 
		#outputFile.flush()
		r.userTwitterStats()
		
	
	except arg:
		print 'Arguments parser error ' + arg
	finally:
		#outputFile.close()
		print '\nDone...\n'


if __name__ == '__main__':
	main(sys.argv[1:]) #1: refers to parameters needed to be supplied