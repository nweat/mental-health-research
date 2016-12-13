__author__ = 'nweat'

try:
	import json
except ImportError:
	import simplejson as json

import data_manager,sys,getopt,codecs,tweepy,yaml,os,os.path

def main(argv):
	ifile = ''
	ifile2 = ''
	ifile3 = ''
	ifile4 = ''
	ifile5 = ''
	ofile = ''
	stats = ''
	normalusers = ''
	pstats = ''
	illness = ''
	matrix = ''
	processed_diagnosed_users = []

	config = open('config.yaml')
	dataMap = yaml.safe_load(config)
	ACCESS_TOKEN = dataMap['TwitterCredentials']['ACCESS_TOKEN']
	ACCESS_SECRET = dataMap['TwitterCredentials']['ACCESS_SECRET']
	CONSUMER_KEY = dataMap['TwitterCredentials']['CONSUMER_KEY']
	CONSUMER_SECRET = dataMap['TwitterCredentials']['CONSUMER_SECRET']
	config.close()

	"""
	GLOBAL VARIABLES
	"""
	path = os.path.join(os.getcwd(), "data_manager/data/seed_nodes.txt")

	if len(argv) == 0:
		print 'You must pass some parameters'
		return

	try:
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
		api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
		myStreamListener = data_manager.manager.TwitterStreamListener(500, path) # pass file and limit of sample normal user candidates to write to file
		myStream = tweepy.Stream(auth = api.auth, listener = myStreamListener)

		helper_obj = data_manager.manager.HelperManager()
		stats_obj = data_manager.manager.StatsManager(api)
		normal_user_obj = data_manager.manager.NormalUsersManager(api, myStream)
		
		opts, args = getopt.getopt(argv, "", ("ifile=","ifile2=","ifile3=","ifile4=","ifile5=","ofile=","stats=","illness=","normalusers=","pstats=","matrix="))
				
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
			elif opt == '--pstats':
				pstats = arg
			elif opt == '--matrix':
				matrix = arg
			elif opt == '--ifile2':
				ifile2 = arg
			elif opt == '--ifile3':
				ifile3 = arg
			elif opt == '--ifile4':
				ifile4 = arg
			elif opt == '--ifile5':
				ifile5 = arg

		if stats and illness:
			# python main.py --ifile data_manager/data/diagnosed_users_in.csv --stats 1 --illness anxiety --ofile data_manager/data/out.json
			inputFile = codecs.open(ifile, 'r', encoding = "utf-8")
			outputFile = codecs.open(ofile, "w+", "utf-8")
			print "\n******Extracting twitter users who made diagnosis statements******"    
			diagnosed_users = stats_obj.extractDiagnosedUsers(inputFile)
			if diagnosed_users:
				print "Done extracting users..."
				inputFile.close()

			print "\n******Generating stats for twitter users who made diagnosis statements******"
			processed_diagnosed_users = stats_obj.generateStats(illness, diagnosed_users)
			outputFile.write(json.dumps(processed_diagnosed_users, sort_keys = True, indent=4, ensure_ascii=False, separators=(',', ':'), default = helper_obj.myconverter))
			print '\n%s Results added to file\n' % len(processed_diagnosed_users)
			outputFile.close()
		elif normalusers and ofile:
		   outputFile = codecs.open(ofile, "w+", "utf-8")

		   print '\n******Retrieving sample twitter users******'
		   normal_user_obj.selectSampleTwitterUsers()
		   if os.path.exists(path):
			print "Done writing to file..."

		   print '\n******Retrieving random seed nodes from file******'
		   seed_node = normal_user_obj.selectRandomSeedNodes(path, 10)
		   print seed_node

		   print '\n***Conducting breadthTraversal to retrieve random number of filtered followers based on limit and depth **'
		   normal_user_obj.breadthTraversal(seed_node, outputFile, 100, 4, 1)
		   outputFile.close()
		elif pstats:
			stats = stats_obj.statsPandas(ifile)
			print stats
		elif matrix:
			inputFile = codecs.open(ifile, 'r', encoding = "utf-8")
			inputFile2 = codecs.open(ifile2, 'r', encoding = "utf-8")
			inputFile3 = codecs.open(ifile3, 'r', encoding = "utf-8")
			inputFile4 = codecs.open(ifile4, 'r', encoding = "utf-8")
			inputFile5 = codecs.open(ifile5, 'r', encoding = "utf-8")

			print "\n******Extracting twitter users who made diagnosis statements******"    
			anxiety_diagnosed_users = stats_obj.extractDiagnosedUsers(inputFile)
			bipolar_diagnosed_users = stats_obj.extractDiagnosedUsers(inputFile2)
			bpd_diagnosed_users = stats_obj.extractDiagnosedUsers(inputFile3)
			ptsd_diagnosed_users = stats_obj.extractDiagnosedUsers(inputFile4)
			depression_diagnosed_users = stats_obj.extractDiagnosedUsers(inputFile5)
			if anxiety_diagnosed_users and bipolar_diagnosed_users and bpd_diagnosed_users and ptsd_diagnosed_users and depression_diagnosed_users:
				print "Done extracting users..."
				inputFile.close()
				inputFile2.close()
				inputFile3.close()
				inputFile4.close()
				inputFile5.close()

			a = stats_obj.generataFrequencyMatrixBasedOnIllnessMentionsByUser(anxiety_diagnosed_users, 'anxiety')
			b = stats_obj.generataFrequencyMatrixBasedOnIllnessMentionsByUser(bipolar_diagnosed_users, 'bipolar')
			c = stats_obj.generataFrequencyMatrixBasedOnIllnessMentionsByUser(bpd_diagnosed_users, 'bpd')
			d = stats_obj.generataFrequencyMatrixBasedOnIllnessMentionsByUser(ptsd_diagnosed_users, 'ptsd')
			e = stats_obj.generataFrequencyMatrixBasedOnIllnessMentionsByUser(depression_diagnosed_users, 'depression')
			stats_obj.sumIndividualMatrices(a,b,c,d,e)
			#python main.py --ifile data_manager/data/diagnosed_users_in_anxiety.csv --ifile2 data_manager/data/diagnosed_users_in_bipolar.csv --ifile3 data_manager/data/diagnosed_users_in_BPD.csv --ifile4 data_manager/data/diagnosed_users_in_PTSD.csv --ifile5 data_manager/data/diagnosed_users_in_depression.csv --matrix 1 > testing.json

	except arg:
		print 'Arguments parser error ' + arg
	except KeyboardInterrupt:
		print '\nGoodbye!'

	finally:
		print 'All done.. Goodbye!!'


if __name__ == '__main__':
	main(sys.argv[1:])