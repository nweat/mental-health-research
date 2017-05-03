import tweepy, sys, json, os, os.path
import HelperManager as helper

"""
REFERENCES:
http://stackoverflow.com/questions/23531608/how-do-i-save-streaming-tweets-in-json-via-tweepy
"""

class TwitterStreamListener(tweepy.StreamListener):
	
	def __init__(self, limit, path, api = None):
		super(TwitterStreamListener, self).__init__()
		self.num_tweets = 0
		self.limit = limit
		self.path = path
		self.helper = helper.HelperManager()
		self.file = ''	

	def on_connect(self):
		if not os.path.exists(self.path):
			self.file = open(self.path, 'w')
		else:
			self.file = open(self.path, 'w+')

	def on_status(self, status):
		lat = 'NaN'
		lon = 'NaN'

		if status.coordinates != None:
			lon = status.coordinates['coordinates'][0] #long
			lat = status.coordinates['coordinates'][1] #lat

		if status.place != None:
			countryCode = status.place.country_code

		record = {'Text': status.text, 'Created At': status.created_at, 
		'stat count': status.user.statuses_count,
		'desc': status.user.description,
		'screen name': status.user.screen_name,
		'lang': status.user.lang,
		'lat': lat,
		'lon': lon }
		

		#self.num_tweets += 1

		if self.num_tweets <= self.limit:
			if self.helper.criteria_normal_user_selection(status.user.statuses_count, status.user.description,status.user.screen_name,status.user.lang,'null','null',lat) == 1:
				self.file.write(status.user.screen_name)
				self.file.write('\n')
				self.num_tweets += 1
				print record
				return True
		else:
			self.file.close()
			return False

	def on_error(self, status_code):
		print('Got an error with status code: ' + str(status_code))
		return True # To continue listening
 
	def on_timeout(self):
		print('Timeout...')
		return True # To continue listening
