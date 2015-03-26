__author__ = 'lekez2005'

import flask,os, json
from xbee import XBee
import serial
from keys.gen_key import generate
from flask_sqlalchemy import SQLAlchemy
from devices import encoder
from devices.device import Devices, load_modules

#from OpenSSL import SSL
#context = SSL.Context(SSL.SSLv23_METHOD)
#context.use_privatekey_file('keys/server.key')
#context.use_certificate_file('keys/server.crt')

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


#xbees
ser = None
xbee = None


@app.route('/', methods=['GET'])
def index():
	return json.dumps([{'Doors': 'Front door'}])


@app.route('/modules', methods=['GET'])
def get_modules():
	return load_modules()


def process_xbee(data):
	from devices.rfid import Rfid
	if 'rf_data' in data:
		raw_message = data.get('rf_data').split('#')
		device = raw_message[0]
		identifier = raw_message[1]
		if device == Devices.RFID:
			try:
				rfid = Rfid.query.get(identifier)
				if rfid is not None:
					rfid.react(raw_message[2])
			except Exception, e:
				print e
		print data


def start_server(regenerate=False):
	# https setup
	ip, server_crt, server_key = generate(regenerate)
	context = (server_crt, server_key)

	#xbees
	#ser = serial.Serial('/dev/ttyUSB0', 9600)
	#xbee = XBee(ser, callback=process_xbee)

	from devices.rfid import rfid
	app.register_blueprint(rfid, url_prefix='/rfid')

	print get_modules()




	port = int(os.environ.get('PORT', 5000))
	try:
		app.run(host=ip, port=port, debug=True, ssl_context=context, use_reloader=False)
	finally:
		print "Force closed"
		xbee.halt()
		ser.close()


if __name__=="__main__":
	start_server(False)