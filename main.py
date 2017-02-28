__author__ = 'nweat'

try:
	import json
except ImportError:
	import simplejson as json

import data_manager,sys,getopt,codecs,tweepy,yaml,os,os.path,csv,sqlite3


def createConnection(db_file):
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except sqlite3.Error as er:
		print(er)
 
	return None
	

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
	illness2 = ''
	matrix = ''
	partition = ''
	patient_timeline = ''
	jsonf = ''
	jsonPatientInfo = ''
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
		#myStreamListener = data_manager.manager.TwitterStreamListener(500, path) # pass file and limit of sample normal user candidates to write to file
		#myStream = tweepy.Stream(auth = api.auth, listener = myStreamListener)

		helper_obj = data_manager.manager.HelperManager()
		stats_obj = data_manager.manager.StatsManager(api)
		#normal_user_obj = data_manager.manager.NormalUsersManager(api, myStream)
		
		opts, args = getopt.getopt(argv, "", ("jsonPatientInfo=","jsonf=","patient_timeline=","illness2=","partition=","ifile=","ifile2=","ifile3=","ifile4=","ifile5=","ofile=","stats=","illness=","normalusers=","pstats=","matrix="))
				
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
			elif opt == '--partition':
				partition = arg
			elif opt == '--illness2':
				illness2 = arg
			elif opt == '--patient_timeline':
				patient_timeline = arg
			elif opt == '--jsonf':
				jsonf = arg
			elif opt == '--jsonPatientInfo':
				jsonPatientInfo = arg

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

		#################################################################BUILD NORMAL USERS NETWORK
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

		#################################################################PATIENTS TWEET ANALYSIS
		#partition data focusing on bipolar, depression and with anxiety
		#python main.py --ifile data_manager/data/diagnosed_users_in_depression.csv --partition 1 --illness 'depression' --illness2 'anxiety' --ofile depression_comorbid.csv
		#python main.py --ifile data_manager/data/diagnosed_users_in_depression.csv --partition 1 --illness 'depression' --illness2 'anxiety' --ofile depression_comorbid.csv
		elif partition and illness:
			inputFile = codecs.open(ifile, 'r', encoding = "utf-8")
			f = open(ofile, 'wb')
			writer = csv.writer(f, quoting = csv.QUOTE_ALL)
			writer.writerow(["username","text","date"])
			print "\n******Extracting twitter users who made diagnosis statements******"    
			diagnosed_users = stats_obj.extractDiagnosedUsers(inputFile)
			if diagnosed_users:
				print "Done extracting users..."
				inputFile.close()
			stats_obj.tagDataForTextMiningTask(diagnosed_users, writer, illness, illness2)
			f.close()
		#
		elif patient_timeline and illness: # and jsonf and jsonPatientInfo
			# python main.py --ifile patient_tweet_analysis/bipolar_comorbid/bipolar_comorbid.csv --patient_timeline 1 --ofile patient_tweet_analysis/bipolar_comorbid_patient_tweets.csv --jsonf patient_tweet_analysis/bipolar_comorbid_patient_tweets.json
			# python main.py --ifile patient_tweet_analysis/bipolar/bipolar.csv --patient_timeline 1 --illness bipolar
			
			#outputJSON = codecs.open(jsonf, "w+", "utf-8")
			#outputJSONPatientInfo = codecs.open(jsonPatientInfo, "w+", "utf-8")

			#csv_output = open(ofile, 'wb')
			#writer = csv.writer(csv_output, quoting = csv.QUOTE_ALL)
			#writer.writerow(["userid","screeName","lang","tweetID","tweetCreated","tweetText","favorites","retweet"])

			conn = createConnection('data_manager/data/sqlite/patient_tweets.sqlite')
			print "\n******Processing patient timelines******"  
			diagnosed_users = stats_obj.getPatientNames(ifile)
			stats_obj.getTweetsPerPartition(diagnosed_users, conn, illness) 

			#outputJSON.write(json.dumps(tweets['tweets'], sort_keys = True, indent=4, ensure_ascii=False, separators=(',', ':'), default = helper_obj.myconverter))
			#outputJSONPatientInfo.write(json.dumps(tweets['patientInfo'], sort_keys = True, indent=4, ensure_ascii=False, separators=(',', ':'), default = helper_obj.myconverter))
			
			#csv_output.close() #csv format
			#outputJSON.close() #json format
			#outputJSONPatientInfo.close()

		#################################################################BUILD MATRIX TO SEE COMORBID PATIENTS
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