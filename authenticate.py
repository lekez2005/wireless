__author__ = 'lekez2005'

from functools import wraps
from flask import request, Response


def check_auth(userid, token):
	"""This function is called to check if a username /
	password combination is valid.
	"""
	# TODO implement authentication here
	return userid == 'admin' and token == 'secret'


def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
		'Invalid UserId or token', 401,
		{'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		userid = request.headers['userid']
		token = request.headers['token']
		if not (userid and token and check_auth(userid, token)):
			return authenticate()
		return f(*args, **kwargs)

	return decorated