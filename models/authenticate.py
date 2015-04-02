__author__ = 'lekez2005'

from functools import wraps
from flask import request, Response, abort


def check_auth(userid, token):
	"""This function is called to check if a username /
	password combination is valid.
	"""
	from user import User
	try:
		u = User.query.get(userid)
		return (u.token == token) and u.authorized
	except:
		return False


def authenticate():
	"""Sends a 401 response that enables basic auth"""
	abort(401)


def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		print 'Attempted auth'
		try:
			userid = request.headers['user_id']
			token = request.headers['token']
		except KeyError, e:
			print e
			abort(401)
		if not (userid and token and check_auth(userid, token)):
			return authenticate()
		return f(*args, **kwargs)

	return decorated