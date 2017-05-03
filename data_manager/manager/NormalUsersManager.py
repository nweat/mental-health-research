try:
	import json
except ImportError:
	import simplejson as json

import datetime, tweepy, math, random, time
from collections import Counter
import HelperManager as helper
from .. import models
import os

"""
REFERENCES: 
https://github.com/ptwobrussell/Recipes-for-Mining-Twitter/blob/master/recipe__crawl.py
https://www.safaribooksonline.com/library/view/mining-the-social/9781449368180/ch09.html
https://en.wikipedia.org/wiki/Reservoir_sampling
http://stackoverflow.com/questions/21308762/avoid-twitter-api-limitation-with-tweepy
"""

class NormalUsersManager:

	def __init__(self, twitter, twitter_stream):
		self.model = models.Keywords()
		self.twitter = twitter
		self.twitter_stream = twitter_stream
		self.helper = helper.HelperManager()


	def selectSampleTwitterUsers(self):
		"""
		:Description: select creators of most recent 1000 sample tweets and save to file as normal users
		"""
		self.twitter_stream.sample()


	def selectRandomSeedNodes(self, path, numOfseeds = 1):
		"""
		:Description: select random seeds from normal users
		:param path: path to file with normal users
		:param numOfseeds: random number of seeds to retrieve
		:return: array of random seed nodes
		"""
		random_seeds = []

		if os.path.exists(path):
			with open(path) as in_file:
				for line in in_file:
					random_seeds.append(line.strip('\n'))
		return random.sample(random_seeds, numOfseeds)  

	
	def getRandomFollowers(self, screeName, limit = 100, sampleSize = 4):
		"""
		:Description: returns a random subset of filtered followers of a specifed user
		:param userID: specifed user
		:param limit: number of followers to return
		:param sampleSize: select subset of n filtered followers e.g. if sampleSize = 4 then return n/4 random samples
		:return: random subset of followers
		"""
		ids = []
		
		for user in tweepy.Cursor(self.twitter.followers, screen_name = screeName).items(limit):
			try:
				if self.helper.criteria_normal_user_selection(user.statuses_count, user.description, user.screen_name, user.lang, user.id_str, ids) == 1:
					ids.append(user.screen_name)

			except tweepy.TweepError as e:
				print 'I just caught the exception: %s' % str(e)
				continue

		return random.sample(ids, (len(ids)/sampleSize))

		

	def breadthTraversal(self, seedNodes, outputFile, limit = 100, sampleSize = 4, depth = 1):
		"""
		:Description: build a network of random sample of normal users starting from seed nodes
		:param seedNodes: starting nodes
		:param limit: number of followers to return
		:param sampleSize: select subset of n filtered followers e.g. if sampleSize = 4 then return n/4 random samples
		:param depth: limit network traversal e.g. depth 1 will build a random network of seed nodes' followers
		:return: random networks of followers
		"""
		flimit = limit
		fsampleSize = sampleSize

		for sn in seedNodes:
			try:
				next_queue = self.getRandomFollowers(sn, flimit, fsampleSize)
				outputFile.write('%s\n' % (sn))

				d = 1
				while d <= depth:
					print '\nDepth: %d' % d
					#outputFile.write('\nDepth: %d' % d)
					d += 1
					(queue, next_queue) = (next_queue, [])
					for _fid in queue:
						_follower_ids = self.getRandomFollowers(_fid, flimit, fsampleSize)

						if _follower_ids != None or len(_follower_ids) != 0:
							outputFile.write('%s\n:' % (_fid))
							print '\n%d random sample followers of %s:' % (len(_follower_ids),_fid)

							for ids in _follower_ids:
								outputFile.write('%s\n' % (ids))
								print '\nrandom sample follower of %s: %s' % (_fid, ids)
							next_queue += _follower_ids
						else:
							#outputFile.write('\n\nFollowers not found for %s, maybe protected acount' % _fid)
							print 'Followers not found for %s, maybe protected acount' % _fid
			except Exception as e:
				print 'I just caught the exception: %s' % str(e)
				continue
		return True

		
