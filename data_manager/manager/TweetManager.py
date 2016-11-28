__author__ = 'nweat'
###############################
#DESCRIPTION:
#1 Read twitter user list who stated "I was diagnosed with depression" from CSV file and produce some stats
#diagnosed users were retreived based on query search through command line: 
# python Exporter.py --querysearch 'I was diagnosed with depression' --since 2014-10-20 --until 2016-10-20

#2 order tweets by username since some users make multiple diagnosis statement

#Get count of tweets posted from
# 1 year back <= date statement made => to now
# also show total tweets including retweets

#label users to see what illness they are referring to, if user is advocate, check if most tweets are English
#get normal users atleast 1000, make sure has enough tweets more than 200, randomly select users and
#check that their description does not contain anything about mentall illness or depression or anxiety
#get proportion of normal users to depressed users 
###############################
try:
	import json
except ImportError:
	import simplejson as json

import sys,math,random,datetime as DT,numpy as np
from time import sleep, strftime, time
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
from urllib2 import HTTPError
from collections import Counter
from .. import models

class TweetManager:
	
	def __init__(self,twitter,twitter_stream):
		self.results = 0
		self.model = models.Keywords()
		self.twitter = twitter
		self.twitter_stream = twitter_stream
		
	#diagnosis statements extracted using Getoldtweets package to retreive more tweets
	def extractDiagnosedUsers(self, file):
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

	def userTwitterStats(self):
		print "\n******Searching for users******"
		print self.model.disease_list
		#users = diagnosed_users['username']
		#for n in range(0, len(users), 100):
			#getUsers = t.users.lookup(screen_name=','.join(users[n:n+100]), _timeout=1)

	def generate_stats(self, illness, diagnosed_users, twitter, outputFile = ''):
		hashtag_mentions = []
		total_anxiety_mentions = total_bipolar_mentions = total_seasonal_disorder = total_ptsd = total_major_depression = total_pmdd = total_situational = total_schizophrenia = 0
		total_advocates = total_survivor = 0
		final = []

		try:

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
		
				usrObj = twitter.users.show(screen_name = usr['username'], _timeout=1)
				print usr['username']
				NumMentionsDiagnosis = len(usr['mentions'].split())

				#http://stackoverflow.com/questions/12452678/fastest-way-to-count-number-of-occurrences-in-a-python-list
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
					if value in (usrObj['description']).lower():
						AdvocateRefDesc += 1
						total_advocates += 1

				#get occurences of mentions of depression related keywords in description
				for idx, value in enumerate(self.model.depression_keywords):
					if value in (usrObj['description']).lower():
						DepressionRefDesc += 1

					if value in (usr['text']).lower():
						DepressionRefDiagnosis += 1

				for idx, value in enumerate(self.model.survivor_keywords):
					if value in (usrObj['description']).lower():
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
				'acctCreated': usrObj['created_at'],
				'usrDesc': usrObj['description'],
				'location': usr['geo'],
				'illness_type': illness,
				'diagnosisMade': usr['date_of_diagnosis'],
				'diagnosisStatement': usr['text'],
				'retweets': usr['retweets'],
				'favorites': usr['favorites'],
				'mentions': usr['mentions'],
				'hashtags': usr['hashtags'],
				'diagnosislink': usr['link'],
				'numTweetsPosted': usrObj['statuses_count'],
				'numFavorites': usrObj['favourites_count'],
				'numFollowers': usrObj['followers_count'],
				'numFriends':  usrObj['friends_count'],
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
        #resp = urllib.request.urlopen(req).read(amt=3)
		except (TwitterHTTPError, Exception, HTTPError) as exc:
			print 'I just caught the exception: %s' % exc
			


	def test_rate_limit(api, wait=True, buffer=.1):
		"""
		REFERENCE: http://stackoverflow.com/questions/21308762/avoid-twitter-api-limitation-with-tweepy
		Tests whether the rate limit of the last request has been reached.
		:param api: The `tweepy` api instance.
		:param wait: A flag indicating whether to wait for the rate limit reset
					 if the rate limit has been reached.
		:param buffer: A buffer time in seconds that is added on to the waiting
					   time as an extra safety margin.
		:return: True if it is ok to proceed with the next request. False otherwise.
		"""
		#Get the number of remaining requests
		remaining = int(api.last_response.getheader('x-rate-limit-remaining'))
		#Check if we have reached the limit
		if remaining == 0:
			limit = int(api.last_response.getheader('x-rate-limit-limit'))
			reset = int(api.last_response.getheader('x-rate-limit-reset'))
			#Parse the UTC time
			reset = datetime.fromtimestamp(reset)
			#Let the user know we have reached the rate limit
			print "0 of {} requests remaining until {}.".format(limit, reset)

			if wait:
				#Determine the delay and sleep
				delay = (reset - datetime.now()).total_seconds() + buffer
				print "Sleeping for {}s...".format(delay)
				sleep(delay)
				#We have waited for the rate limit reset. OK to proceed.
				return True
			else:
				#We have reached the rate limit. The user needs to handle the rate limit manually.
				return False 
		#We have not reached the rate limit
		return True



	#specify some basic criteria for selecting normal users
	def criteria_normal_user_selection(self, status_count, description, screen_name, lang, id = 'null', existing_id = 'null'):
		DiseaseRefDesc = 0
		AdvocateRefDesc = 0
		DepressionRefDesc = 0
		status = 0

		if description:
			for idx, value in enumerate(self.model.disease_list):
				if value in ((description).lower() or (screen_name).lower()):
					DiseaseRefDesc += 1
			for idx, value in enumerate(self.model.advocate_keywords):
				if value in ((description).lower() or (screen_name).lower()):
					AdvocateRefDesc += 1
			for idx, value in enumerate(self.model.depression_keywords):
				if value in ((description).lower() or (screen_name).lower()):
					DepressionRefDesc += 1

		if existing_id != 'null':
			if (id not in existing_id) and status_count >= 200 and DiseaseRefDesc == 0 and AdvocateRefDesc == 0 and DepressionRefDesc == 0 and lang == 'en':
				status = 1
		else:
			if status_count >= 200 and DiseaseRefDesc == 0 and AdvocateRefDesc == 0 and DepressionRefDesc == 0 and lang == 'en':
				status = 1
		return status

	#select random seed node from random sample of recent tweets
	def select_random_seed_node(self, limit = 100, numOfseed = 1):
		random_users = []
		cnt = 0

		for i, tweet in enumerate(self.twitter_stream.statuses.sample()):
			if 'user' in tweet:
				if self.criteria_normal_user_selection(tweet['user']['statuses_count'], tweet['user']['description'],tweet['user']['screen_name'],tweet['user']['lang'],'null','null') == 1:
					#print tweet['user']['screen_name']
					#print tweet['user']['description']
					#print tweet['user']['statuses_count']
					#print tweet['user']['id_str']
					#print tweet['user']['lang']
					#print '\n\n'
					random_users.append(tweet['user']['id_str'])
					cnt += 1
					if cnt == limit:
						break			
		return random.sample(random_users, numOfseed) 


	"""
	REFERENCES: 
	https://github.com/ptwobrussell/Recipes-for-Mining-Twitter/blob/master/recipe__crawl.py
	https://www.safaribooksonline.com/library/view/mining-the-social/9781449368180/ch09.html
	https://en.wikipedia.org/wiki/Reservoir_sampling
	
	DESCRIPTION: returns a random subset of filtered followers
	
	PARAMETERS: 
	limit - should be in group of 20s e.g. 20, 40, 60 as followers are returned in groups of 20s
	sampleSize - select subset of n filtered followers e.g. if 1/3 => n/3
	""" 
	def get_random_followers_ids(self, user_id, limit = 100, sampleSize = 4):
		#print self.twitter.response.headers.get('h')
		try:
			cursor = -1
			ids = []
			while cursor != 0:
				response = self.twitter.followers.list(user_id = user_id, cursor = cursor)

				if response is not None:
					cursor = response['next_cursor']
					for i, usr in enumerate(response['users']):
						
						if self.criteria_normal_user_selection(usr['statuses_count'],usr['description'],usr['screen_name'],usr['lang'],usr['id_str'],ids) == 1:
							#print '%d %s, %s' % (i, usr['screen_name'], usr['id_str'])
							ids.append(usr['id_str'])

				if len(ids) >= limit or response is None:
					cursor = 0

			return random.sample(ids, (len(ids)/sampleSize))

		except (TwitterHTTPError, Exception, HTTPError) as exc:
			print 'I just caught the exception: %s' % exc
			sleep(180)


	def breadth_traversal(self, follower_ids, output, limit = 100, depth = 1):
		normal_users = []

		try:
			for fid in follower_ids:
				next_queue = self.get_random_followers_ids(fid, limit)
				#screen_name = self.twitter.users.show(user_id=fid)['screen_name']
				print '\nseed_node: %s'% fid
				output.write('\nseed_node: %s' % (fid))
				#normal_users.append(fid

				d = 1
				while d <= depth:
					print '\n\nDepth: %d' % d
					d += 1
					(queue, next_queue) = (next_queue, [])
					for _fid in queue:
						_follower_ids = self.get_random_followers_ids(user_id=_fid, limit=limit)
				
						#screen_name = self.twitter.users.show(user_id=_fid)['screen_name']
						output.write('\n%d random followers of %s:' % (len(_follower_ids),_fid))
						print '\n%d random followers of %s:' % (len(_follower_ids),_fid)
						#normal_users.append(_fid)
						#normal_users.append(_follower_ids)

						#getfollowers = self.twitter.users.lookup(user_id=','.join(map(str, _follower_ids)))
						for ids in _follower_ids:
							output.write('\nfollower of %s: %s' % (_fid, ids))
							print '\nfollower of %s: %s' % (_fid, ids)
							

						next_queue += _follower_ids
			return normal_users

		except (TwitterHTTPError, HTTPError) as exc:
			print 'I just caught the exception2: %s' % exc
			#time.sleep(300)
			#continue

#print json.dumps(tweet, indent=4)  
#python twitter_streaming.py > twitter_stream_1000tweets.txt
"""
#if usr['username'] not in track_user_exists:
					#tweets posted within one year up to diagnosis posted check if atleast 300
				#dateDiagnosed = DT.datetime.strptime(usr['date_of_diagnosis'], "%d/%m/%Y %H:%M")
				#since = dateDiagnosed.replace(year=dateDiagnosed.year-1)
				#since = since.strftime('%Y-%m-%d')
				#until = dateDiagnosed#.replace(day=dateDiagnosed.day+1)
				#until = until.strftime('%Y-%m-%d')
				#NumTweetsYrUpToDiagnosis = got.manager.TweetCriteria().setUsername(usr['username']).setSince(since).setUntil(until).setMaxTweets(200)
				#NumTweetsYrUpToDiagnosis = len(got.manager.TweetManager.getTweets(NumTweetsYrUpToDiagnosis))
"""