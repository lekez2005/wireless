__author__ = 'lekez2005'

from functools import wraps
from flask import request, Response, abort

# import RPi.GPIO as GPIO
#
# GPIO.setmode(GPIO.BCM)
#
# AUTH_BUTTON = 21
# AUTH_LED = 20

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


def send_401():
	"""Sends a 401 response that enables basic auth"""
	abort(401)


def authenticate():
	pass



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
			return send_401()
		return f(*args, **kwargs)

	return decorated