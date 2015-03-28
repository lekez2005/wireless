__author__ = 'lekez2005'

import json
from json import JSONEncoder
from sqlalchemy.orm.state import InstanceState

class Encoder(JSONEncoder):
	def default(self, o):
		if isinstance(o, InstanceState):
			pass
		elif isinstance(o, list):
			return list(o)
		else:
			return json.JSONEncoder.default(self, o)