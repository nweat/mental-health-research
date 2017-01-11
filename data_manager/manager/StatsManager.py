#try:
#	import json
#except ImportError:
#	import simplejson as json
import simplejson as json
import datetime, tweepy, pprint, csv
import numpy as np
import pandas as pd
import HTMLParser
from pandas.io.json import json_normalize
from collections import Counter
from .. import models

class StatsManager:
	
	def __init__(self, twitter):
		self.model = models.Keywords()
		self.twitter = twitter
		
	@staticmethod
	def extractDiagnosedUsers(file):
		"""
		NOTE: raw diagnosis statements extracted using Getoldtweets package to retreive more tweets
		"""
		diagnosed_users = []
		for row in file:
			row = row.split(';')
			diagnosed_users.append({
				'username':row[0], 
				'date_of_diagnosis':row[1],
				'retweets':row[2],
				'favorites':row[3],
				'text':row[4],
				'geo':row[5],
				'mentions':row[6],
				'hashtags':row[7],
				'link':row[9]})
		return diagnosed_users[1:]

	@staticmethod
	def getPatientNames(file):
		diagnosed_users = []

		f = open(file, 'rt')
		try:
			reader = csv.reader(f)
			for row in reader:
				diagnosed_users.append(row[0])
			return diagnosed_users[1:]
		finally:
			f.close()

	def getTweetsPerPartition(self, diagnosed_users, csv):
		tweetsJSON = []
		patientInfoJSON = []
		userExists = []
		advocate_check = 0
		page_list =[]

		for usr in diagnosed_users:
			for page in tweepy.Cursor(api.user_timeline, id=usr['username'], count=200).pages(16):
				page_list.append(page)
				n = n+1
				print n

			for page in page_list:
				for status in page:
					print status.text


			advocate_check = 0
			try:
				#https://www.analyticsvidhya.com/blog/2014/11/text-data-cleaning-steps-python/
				#make initial request for most recent tweets (200 is the maximum allowed count)
				userObj = self.twitter.get_user(usr)

				#check if advocate keywords found in description
				for idx, value in enumerate(self.model.advocate_keywords):
					if value in userObj.description.lower():
						advocate_check += 1

				if usr not in userExists:
					#desc = userObj.description.encode("utf-8")
					patientInfoJSON.append({
						'userID': userObj.id_str,
						'userName': userObj.screen_name,
						'userStatusCount': userObj.statuses_count,
						'userDesc': userObj.description,
						'userLang': userObj.lang,
						'userCreated': userObj.created_at,
						'userTimeZone': userObj.time_zone,
						'userLocation': userObj.location,
						'userFriends': userObj.friends_count,
						'userFollowers': userObj.followers_count,
						'advocate': advocate_check
						})
				new_tweets = self.
				.user_timeline(screen_name = usr, count = 200)
				html_parser = HTMLParser.HTMLParser()
				print "\nUser: %s-%s\n" % (userObj.screen_name,userObj.statuses_count)
			except tweepy.TweepError as e:
				print 'I just caught the exception: %s' % str(e)
				continue
			# check MERRYJAUREGUl user to see if code works
			if userObj.statuses_count >= 200 and advocate_check == 0:
				tweets = self.get_all_tweets(usr, new_tweets, csv)
				for tweet in tweets:

					try:
						tweetText = html_parser.unescape(tweet.text)
						#tweetText = tweetText.decode('utf-8').strip()
						tweetsJSON.append({
							'userID': tweet.user.id_str,
							'userName': tweet.user.screen_name,
							'tweetID': tweet.id_str,
							'tweetLang': tweet.lang,
							'tweetCreated': tweet.created_at,
							'tweetText': tweetText,
							'tweetFav': tweet.favorite_count,
							'tweetRT': tweet.retweet_count,
							'tweetEntities': tweet.entities,
							'tweetPlace': tweet.place,
							'tweetCoord': tweet.coordinates # fix
							})
					except Exception as e:
						continue
			else:
				print "Too little tweets or this person could be advocate..check patient info file\n"

			userExists.append(usr)
		return {'tweets': tweetsJSON, 'patientInfo': patientInfoJSON}


	def timeStampAnalysis(self):
		"""
		http://beneathdata.com/how-to/email-behavior-analysis/
		http://stackoverflow.com/questions/40489196/time-series-and-sentiment-analysis-with-pandas-timegrouper
		https://m.reddit.com/r/learnpython/comments/5bsvip/time_series_with_pandas_timegrouper/
		https://rawgit.com/ptwobrussell/Mining-the-Social-Web-2nd-Edition/master/ipynb/html/Chapter%201%20-%20Mining%20Twitter.html
		http://blog.coderscrowd.com/twitter-hashtag-data-analysis-with-python/
		group by times and get sentiment, times depression keywords posted	
		"""
		print 'to be implemented'


	def get_all_tweets(self, screen_name, new_tweets, csv):
		"""
		https://gist.github.com/yanofsky/5436496
		check that users are not duplicated, only get tweets once for a user
		"""
		#Twitter only allows access to a users most recent 3240 tweets with this method
		
		#initialize a list to hold all the tweepy Tweets
		alltweets = []	

		#save most recent tweets
		alltweets.extend(new_tweets)
		
		#save the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1
		
		#keep grabbing tweets until there are no tweets left to grab
		while len(new_tweets) > 0:
			print "getting tweets before %s" % (oldest)

			try:
				#make initial request for most recent tweets (200 is the maximum allowed count)
				new_tweets = self.twitter.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
			except tweepy.TweepError as e:
				print 'I just caught the exception: %s' % str(e)
				continue
			
			#save most recent tweets
			alltweets.extend(new_tweets)
			
			#update the id of the oldest tweet less one
			oldest = alltweets[-1].id - 1
			
			print "...%s tweets downloaded so far" % (len(alltweets))
		#transform the tweepy tweets into a 2D array that will populate the csv	
		outtweets = [[tweet.user.id_str, tweet.user.screen_name, tweet.lang, tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), tweet.favorite_count, tweet.retweet_count] for tweet in alltweets]
		csv.writerows(outtweets)
		return alltweets



	def tagDataForTextMiningTask(self, diagnosed_users, writer, illness, illness2 = ''):
		comorbid_bipolar = 0 # if bipolar and anxiety together
		bipolar = 0 # only bipolar
		comorbid_depression = 0 # if depression and anxiety
		depression = 0 # only depression
		filtered = []
		userExists = []
		patientIds = []

		"""
		checks that illness name is not just a mention with # or @ meaning it is a user with a disease name
		"""

		for usr in diagnosed_users:
			try:
				userObj = self.twitter.get_user(usr['username'])
				patientIds.append(userObj.id_str)
			except tweepy.TweepError as e:
				print 'I just caught the exception: %s' % str(e)
				continue

			userText = usr['text'].lower()
			if illness != '' and illness2 == '': # check for single disease based on illness param
				otherDiseases = 0
				isIllness = 0
				for idx, value in enumerate(self.model.disease_list):
					if value == illness and value in usr['text'].lower() and (userText[userText.index(value) - 1] != '@' or userText[userText.index(value) - 1] != '#'):
						isIllness = 1
					elif value != illness and value in usr['text'].lower() and (userText[userText.index(value) - 1] != '@' or userText[userText.index(value) - 1] != '#'):
						otherDiseases = 1
				if isIllness == 1 and otherDiseases == 0:
					if usr['username'] not in userExists:
						writer.writerow([usr['username'], usr['text']])
						print '%s is %s' % (usr['username'], illness) # save to seperate file for each disease
			elif illness != '' and illness2 != '': # check for comorbid disease based on both params
				isIllness1 = 0
				isIllness2 = 0
				otherDiseases = 0
				for idx, value in enumerate(self.model.disease_list):
					if value == illness and value in usr['text'].lower() and (userText[userText.index(value) - 1] != '@' or userText[userText.index(value) - 1] != '#'):
						isIllness1 = 1
					elif value == illness2 and value in usr['text'].lower() and (userText[userText.index(value) - 1] != '@' or userText[userText.index(value) - 1] != '#'):
						isIllness2 = 1
					elif (value != illness or value != illness2 ) and value in usr['text'].lower() and (userText[userText.index(value) - 1] != '@' or userText[userText.index(value) - 1] != '#'):
						otherDiseases = 1
				if isIllness1 == 1 and isIllness2 == 1 and otherDiseases == 0:
					if usr['username'] not in userExists:
						writer.writerow([usr['username'], usr['text']])
						print '%s is %s and %s' % (usr['username'], illness, illness2) # save to seperate file for each disease
			userExists.append(usr['username'])
		return patientIds
		
 
	def generataFrequencyMatrixBasedOnIllnessMentionsByUser(self, diagnosed_users, illness = ''):
		"""
		NOTE: http://www.linuxtopia.org/online_books/programming_books/python_programming/python_ch20s05.html
		"""
		users_with_multiple_diagnosis = []
		counter = 0
		final = []
		columns = 5
		rows = 5
		matrix = [[0 for i in range(rows)] for j in range(columns)] # build a 5 x 5 matrix

		for usr in diagnosed_users:
			BPD_check = 0
			bipolar_check = 0
			anxiety_check = 0
			depression_check = 0 # combine major and seasonal and situational
			ptsd_check = 0

			for idx, value in enumerate(self.model.disease_list):
				if (value == 'bpd') and value in usr['text'].lower():
					BPD_check = 1
				if (value == 'bipolar disorder' or value == 'bipolar') and value in usr['text'].lower():
					bipolar_check = 1
				if value == 'anxiety' and value in usr['text'].lower():
					anxiety_check = 1
				if (value == 'major depression' or value == 'seasonal depression' or value == 'depression') and value in usr['text'].lower():
					depression_check = 1
				if (value == 'ptsd') and value in usr['text'].lower():
					ptsd_check = 1

			# check if user already made diagnosis statement, then just update his disease mentions
			if usr['username'] in users_with_multiple_diagnosis:
				for f in final:
					if f['screenName'] == usr['username']:
						if (BPD_check != f['bpd']) and f['bpd'] == 0:
							f['bpd'] = BPD_check
						if (bipolar_check != f['bipolar']) and f['bipolar'] == 0:
							f['bipolar'] = bipolar_check
						if (anxiety_check != f['anxiety']) and f['anxiety'] == 0:
							f['anxiety'] = anxiety_check
						if (ptsd_check != f['ptsd']) and f['ptsd'] == 0:
							f['ptsd'] = ptsd_check
						if (depression_check != f['depression']) and f['depression'] == 0:
							f['depression'] = depression_check
					else:
						continue
						
			# add user if not yet exists
			if usr['username'] not in users_with_multiple_diagnosis:
				final.append({
					'screenName': usr['username'],
					'anxiety': anxiety_check,
					'depression': depression_check,
					'bpd': BPD_check,
					'bipolar': bipolar_check,
					'ptsd': ptsd_check
				})
			users_with_multiple_diagnosis.append(usr['username'])
		#print json.dumps(final, indent = 4)

		for j in range(columns):
			for i in range(rows):
				if i == 0: # count users who state anxiety and other disease
					for f in final:
						if j == 0:
							if f['anxiety'] == 1: #and f['bipolar'] == 0 and f['depression'] == 0 and f['bpd'] == 0 and f['ptsd'] == 0
								matrix[i][j] += 1
						if j == 1:
							if f['anxiety'] == 1 and f['depression'] == 1:
								matrix[i][j] += 1
						if j == 2:
							if f['anxiety'] == 1 and f['bipolar'] == 1:
								matrix[i][j] += 1
						if j == 3:
							if f['anxiety'] == 1 and f['bpd'] == 1:
								matrix[i][j] += 1
						if j == 4:
							if f['anxiety'] == 1 and f['ptsd'] == 1:
								matrix[i][j] += 1

				if i == 1: # count users who state depression and other disease
					for f in final:
						if j == 1:
							if f['depression'] == 1:
								matrix[i][j] += 1
								if illness == 'bipolar':
									print f['screenName']
						if j == 2:
							if f['depression'] == 1 and f['bipolar'] == 1:
								matrix[i][j] += 1
						if j == 3:
							if f['depression'] == 1 and f['bpd'] == 1:
								matrix[i][j] += 1
						if j == 4:
							if f['depression'] == 1 and f['ptsd'] == 1:
								matrix[i][j] += 1

				if i == 2: # count users who state bipolar and other disease
					for f in final:
						if j == 2:
							if f['bipolar'] == 1:
								matrix[i][j] += 1
						if j == 3:
							if f['bipolar'] == 1 and f['bpd'] == 1:
								matrix[i][j] += 1
						if j == 4:
							if f['bipolar'] == 1 and f['ptsd'] == 1:
								matrix[i][j] += 1

				if i == 3: # count users who state bpd and other disease
					for f in final:
						if j == 3:
							if f['bpd'] == 1:
								matrix[i][j] += 1
						if j == 4:
							if f['bpd'] == 1 and f['ptsd'] == 1:
								matrix[i][j] += 1

				if i == 4: # count users who state ptsd only
					for f in final:
						if j == 4:
							if f['ptsd'] == 1:
								matrix[i][j] += 1


		print 'Generated matrix for %s\n' % illness
		pprint.pprint(matrix)
		return matrix


	def sumIndividualMatrices(self, m1, m2, m3, m4, m5):
		columns = 5
		rows = 5
		final= [ rows*[0] for i in range(columns) ]

		for i in range(columns):
			for j in range(rows):
				final[i][j]= m1[i][j] + m2[i][j] + m3[i][j] + m4[i][j] + m5[i][j]

		print 'Final matrix \n'
		pprint.pprint(final)
		return final

	

	def generateStats(self, illness, diagnosed_users):
		hashtag_mentions = []
		total_anxiety_mentions = total_bipolar_mentions = total_seasonal_disorder = total_ptsd = total_major_depression = total_pmdd = total_situational = total_schizophrenia = 0
		total_advocates = total_survivor = 0
		final = []

		for usr in diagnosed_users:
			AdvocateRefDesc = 0
			DepressionRefDesc = 0
			DepressionRefDiagnosis = 0
			NumTweetsYrUpToDiagnosis = 0
			SurvivorRefDesc = 0
			SurvivorRefDiagnosis = 0
			NumMentionsDiagnosis = 0
			num_schizophrenia = num_anxiety = num_ptsd = num_bipolar = num_major_depression = seasonal_disorder = num_pmdd = num_situational = 0
			whatyoudontsee = mydepressionlookslike = myanxietylookslike = mentalillnessfeelslike = mentalhealthawarenessday = worldmentalhealthday = depressionawareness = 0
			NumMentionsDiagnosis = len(usr['mentions'].split())

			try:
				usrObj = self.twitter.get_user(screen_name = usr['username'])
				usrCreatedFormat = usrObj.created_at.strftime('%Y-%m-%d %H:%M:%S.%f')
				usrCreated = datetime.datetime.strptime(usrCreatedFormat, '%Y-%m-%d %H:%M:%S.%f')
				print usrObj.screen_name

			except tweepy.TweepError as e:
				print 'I just caught the exception: %s' % str(e)
				continue

			for hashtag in usr['hashtags'].lower().split():
				if hashtag:
					hashtag_mentions.append(hashtag)

			#get occurences of mentions of depression related diseases in diagnosis statement
			for idx, value in enumerate(self.model.disease_list):
				if value == 'anxiety' and value in usr['text'].lower():
					num_anxiety += 1
					total_anxiety_mentions += 1
				if (value == 'bpd' or value == 'bipolar disorder' or value == 'bipolar') and value in usr['text'].lower():
					num_bipolar += 1
					total_bipolar_mentions += 1
				if (value == 'seasonal affective disorder' or value == 'seasonal depression') and value in usr['text'].lower():
					seasonal_disorder += 1
					total_seasonal_disorder += 1
				if (value == 'ptsd') and value in usr['text'].lower():
					num_ptsd += 1
					total_ptsd += 1
				if (value == 'major depression') and value in usr['text'].lower():
					num_major_depression += 1
					total_major_depression += 1
				if (value == 'pmdd') and value in usr['text'].lower():
					num_pmdd += 1
					total_pmdd += 1
				if (value == 'situational depression') and value in usr['text'].lower():
					num_situational += 1
					total_situational += 1
				if (value == 'schizophrenia') and value in usr['text'].lower():
					num_schizophrenia += 1
					total_schizophrenia += 1
				
			#get occurences of mentions of advocate in description
			for idx, value in enumerate(self.model.advocate_keywords):
				if value in (usrObj.description).lower():
					AdvocateRefDesc += 1
					total_advocates += 1

			#get occurences of mentions of depression related keywords in description
			for idx, value in enumerate(self.model.depression_keywords):
				if value in (usrObj.description).lower():
					DepressionRefDesc += 1

				if value in (usr['text']).lower():
					DepressionRefDiagnosis += 1

			for idx, value in enumerate(self.model.survivor_keywords):
				if value in (usrObj.description).lower():
					SurvivorRefDesc += 1
					SurvivorRefDiagnosis += 1
					total_survivor += 1

			for idx, value in enumerate(self.model.hashtags):
				if value == 'whatyoudontsee' and value in usr['hashtags'].lower():
					whatyoudontsee += 1
				if value == 'mydepressionlookslike' and value in usr['hashtags'].lower():
					mydepressionlookslike += 1
				if value == 'myanxietylookslike' and value in usr['hashtags'].lower():
					myanxietylookslike += 1
				if value == 'mentalillnessfeelslike' and value in usr['hashtags'].lower():
					mentalillnessfeelslike += 1
				if value == 'mentalhealthawarenessday' and value in usr['hashtags'].lower():
					mentalhealthawarenessday += 1
				if value == 'worldmentalhealthday' and value in usr['hashtags'].lower():
					worldmentalhealthday += 1
				if value == 'depressionawareness' and value in usr['hashtags'].lower():
					depressionawareness += 1
					
			final.append({
			'screenName': usr['username'],
			'acctCreated': usrCreated,
			'usrDesc': usrObj.description,
			'location': usr['geo'],
			'illness_type': illness,
			'diagnosisMade': usr['date_of_diagnosis'],
			'diagnosisStatement': usr['text'],
			'retweets': usr['retweets'],
			'favorites': usr['favorites'],
			'mentions': usr['mentions'],
			'hashtags': usr['hashtags'],
			'diagnosislink': usr['link'],
			'numTweetsPosted': usrObj.statuses_count,
			'numFavorites': usrObj.favourites_count,
			'numFollowers': usrObj.followers_count,
			'numFriends':  usrObj.friends_count,
			'AdvocateRefDesc': AdvocateRefDesc,
			'DepressionRefDesc': DepressionRefDesc,
			'DepressionRefDiagnosis': DepressionRefDiagnosis,
			'SurvivorRefDesc': SurvivorRefDesc,
			'SurvivorRefDiagnosis': SurvivorRefDiagnosis,
			'NumMentionsDiagnosis': NumMentionsDiagnosis,
			'whatyoudontsee': whatyoudontsee,
			'mydepressionlookslike': mydepressionlookslike,
			'myanxietylookslike': myanxietylookslike,
			'mentalillnessfeelslike': mentalillnessfeelslike,
			'mentalhealthawarenessday': mentalhealthawarenessday,
			'worldmentalhealthday': worldmentalhealthday,
			'depressionawareness': depressionawareness,
			'AnxietyMentions': num_anxiety,
			'BipolarMentions': num_bipolar,
			'PTSDMentions': num_ptsd,
			'seasonal_disorderMentions': seasonal_disorder,
			'num_major_depressionMentions': num_major_depression,
			'num_pmddMentions': num_pmdd,
			'num_situationalMentions': num_situational,
			'num_schizophreniaMentions': num_schizophrenia
			})

		final.append({'overall': {
			'totalReturned': len(final),
			'hashtags': Counter(hashtag_mentions), 
			'total_advocate_mentions': total_advocates,
			'total_survivor_mentions': total_survivor,
			'illness_mentions': [
			{'disease': 'anxiety','count': total_anxiety_mentions},
			{'disease': 'bipolar','count': total_bipolar_mentions},
			{'disease': 'seasonal','count': total_seasonal_disorder},
			{'disease': 'ptsd','count': total_ptsd},
			{'disease': 'major_depression','count': total_major_depression},
			{'disease': 'pmdd','count': total_pmdd},
			{'disease': 'situational_depression','count': total_situational},
			{'disease': 'schizophrenia','count': total_schizophrenia}
			]
			}})
		return final

	def statsPandas(self, ifile):
		with open(ifile) as data_file:
			data = json.load(data_file)
		
		df = pd.DataFrame.from_records(data)
		results = df.groupby(['DiagnosisType', 'mentions'])['numMentions'].max()
		return results.unstack(0)

