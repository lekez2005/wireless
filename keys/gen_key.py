__author__ = 'lekez2005'

from werkzeug.serving import make_ssl_devcert
import socket, os

def generate(regenerate):
	ip = 'localhost'
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8",80))
		ip = s.getsockname()[0]
		s.close()
	except Exception, e:
		print e

	base_dir = os.path.dirname(os.path.realpath(__file__))
	path = os.path.join(base_dir, 'server')
	if regenerate:
		server_crt, server_key = make_ssl_devcert(path, host=ip)
		print 'Key created for ', ip
		return ip, server_crt, server_key
	else:
		server_crt = path + '.crt'
		server_key = path + '.key'
		return ip, server_crt, server_key



