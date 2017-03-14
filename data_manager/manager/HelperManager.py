import datetime, tweepy
from .. import models

class HelperManager:

	def __init__(self):
		self.model = models.Keywords()
		pass

	@staticmethod
	def myconverter(o):
		"""
		serialize datetime objects
		"""
		if isinstance(o, datetime.datetime):
			return o.__str__()
	
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

			#NEED TO CHECK TWEETS FOR DEPRESSION KEYWORDS
			"""
			for user in tweepy.Cursor(self.twitter.followers, screen_name = screen_name).items(limit):
				try:
					
				except tweepy.TweepError as e:
					print 'I just caught the exception: %s' % str(e)
					continue

			try:
				for page in tweepy.Cursor(self.twitter.user_timeline, id=usr, count=200).pages(16):
					page_list.append(page)
			except tweepy.TweepError as e:
				print 'I just caught the exception: %s' % str(e)
				#continue
			"""

		if existing_id != 'null':
			if (id not in existing_id) and status_count >= 200 and DiseaseRefDesc == 0 and AdvocateRefDesc == 0 and DepressionRefDesc == 0 and lang == 'en':
				status = 1
		else:
			if status_count >= 200 and DiseaseRefDesc == 0 and AdvocateRefDesc == 0 and DepressionRefDesc == 0 and lang == 'en':
				status = 1
		return status