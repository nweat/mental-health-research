try:
	import json
except ImportError:
	import simplejson as json

import datetime, tweepy
from collections import Counter
from .. import models
from .. import helpers

class StatsManager:
	
	def __init__(self, twitter, twitter_stream = ''):
		self.model = models.Keywords()
		self.twitter = twitter
		self.twitter_stream = twitter_stream
		
	@staticmethod
	def extractDiagnosedUsers(file):
		"""
		NOTE: diagnosis statements extracted using Getoldtweets package to retreive more tweets
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


	def generate_stats(self, illness, diagnosed_users):
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
