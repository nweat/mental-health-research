import datetime

class Helpers:

	def __init__(self):
		pass

	@staticmethod
	def myconverter(o):
		"""
		serialize datetime objects
		"""
		if isinstance(o, datetime.datetime):
			return o.__str__()
