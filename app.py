__author__ = 'lekez2005'

import os

import flask
from xbee.python2to3 import intToByte, stringToBytes
from xbee import XBee
import serial
from flask_sqlalchemy import SQLAlchemy

from models import pi
from models.authenticate import requires_auth
from keys.gen_key import generate


app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

from models.device import Devices, load_modules

#from OpenSSL import SSL
#context = SSL.Context(SSL.SSLv23_METHOD)
#context.use_privatekey_file('keys/server.key')
#context.use_certificate_file('keys/server.crt')




@app.route('/', methods=['GET'])
def index():
	return flask.jsonify({'Status': 'OK'})


@app.route('/modules', methods=['GET'])
def get_modules():
	return load_modules()

@app.route('/activate', methods=['POST'])
@requires_auth
def activate():
	data = flask.request.get_json(force=True)
	state = data.get('state')
	pi.set_alarm_active(state)
	return flask.jsonify({'Status': 'OK'})

def transmit_message(address, message, verbose=True):
	ad = intToByte(address/256) + intToByte(address%256)
	if verbose:
		print "Send " + message + " to " + str(address)
	xbee.tx(dest_addr=ad, data=stringToBytes(message+'\n'))


def process_xbee(data):
	from models.rfid import Rfid
	from models.detector import Detector

	if 'rf_data' in data:
		raw_message = data.get('rf_data').split('#', 2)
		device = raw_message[0]
		if device == Devices.RFID:
			try:
				identifier = raw_message[1]
				rfid = Rfid.query.get(identifier)
				if rfid is not None:
					rfid.react(raw_message[2])
			except Exception, e:
				print e
		elif device == Devices.DETECTOR:
			try:
				identifier = raw_message[1]
				det = Detector.query.get(identifier)
				if det is not None:
					det.react(raw_message[2])
			except Exception, e:
				print e
		print data

#xbees
ser = serial.Serial('/dev/ttyUSB0', 9600)
xbee = XBee(ser, callback=process_xbee)

def start_server(regenerate=False):
	# https setup
	ip, server_crt, server_key = generate(regenerate)
	context = (server_crt, server_key)


	pi.setup()

	from models.rfid import rfid
	from models.door import door_blueprint
	from models.alarm import alarm_blueprint
	from models.detector import detector_blueprint
	from models.user import user_blueprint
	app.register_blueprint(rfid, url_prefix='/rfid')
	app.register_blueprint(door_blueprint, url_prefix='/door')
	app.register_blueprint(alarm_blueprint, url_prefix='/alarm')
	app.register_blueprint(detector_blueprint, url_prefix='/detector')
	app.register_blueprint(user_blueprint, url_prefix='/user')

	print get_modules()




	port = int(os.environ.get('PORT', 5000))
	try:
		pi.display(ip, 1)
		app.run(host=ip, port=port, debug=True, ssl_context=context, use_reloader=False)
	finally:
		pi.lcd.clear()
		pi.display('Closing')
		print "Force closed"
		xbee.halt()
		ser.close()
		pi.clean_up()


if __name__=="__main__":
	start_server(False)