import tweepy,math,random

class NormalUsersManager:

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