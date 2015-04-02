__author__ = 'lekez2005'

from flask import Blueprint, request, jsonify
from authenticate import requires_auth
import json

import sys

sys.path.insert(0, '../')
from app import db

from device import Devices
from encoder import Encoder

#db = SQLAlchemy()

class Alarm(db.Model):
	identifier = db.Column(db.String(50), primary_key=True)
	pretty_name = db.Column(db.String(50))
	device_type = db.Column(db.String(50), default=Devices.ALARM)
	description = db.Column(db.Text)
	active = db.Column(db.Boolean, default=True)

	def __init__(self, identifier, description, pretty_name=None):
		self.identifier = identifier
		self.description = description

		if pretty_name is None:
			self.pretty_name = identifier
		else:
			self.pretty_name = pretty_name

	@classmethod
	def load_to_dict(cls, modules):
		try:
			alarms = cls.query.filter_by(active=True).all()
			if alarms is not None:
				modules[Devices.ALARM] = []
				for al in alarms:
					modules[Devices.ALARM].append((al.identifier, al.pretty_name))
		except Exception, e:
			print e




	def __repr__(self):
		return '<Alarm: %s, %s>' % (self.identifier, self.description)

	def react(self, message):
		pass

	def ring(self):
		print "Alarm ringing"

	def stop(self):
		print "Stopping alarm"


class JsonEncoder(Encoder):
	def default(self, o):
		if not isinstance(o, Alarm):
			return super(JsonEncoder, self).default(o)
		return o.__dict__

alarm_blueprint = Blueprint('alarm', __name__)

@alarm_blueprint.route('/<identifier>')
@requires_auth
def get_alarm(identifier):
	a = Alarm.query.get_or_404(identifier)
	resp = json.loads(json.dumps(a, cls=JsonEncoder))
	resp['Status'] = 'OK'
	resp['detectors'] = [ [det.identifier, det.pretty_name]  for det in a.detectors]
	return jsonify(resp)

@alarm_blueprint.route('/update', methods=['POST'])
@requires_auth
def update_card():
	data = request.get_json(force=True)
	c = Alarm.query.get_or_404(data.get('identifier'))
	c.pretty_name = data.get('pretty_name')
	c.valid = data.get('valid')
	c.description = data.get('description')
	db.session.add(c)
	db.session.commit()
	return json.dumps({'Status': 'OK'})

@alarm_blueprint.route('/ring/<identifier>', methods=['GET'])
@requires_auth
def ring_alarm(identifier):
	a = Alarm.query.get_or_404(identifier)
	a.ring()
	return jsonify({'Status': 'OK'})

@alarm_blueprint.route('/stop/<identifier>', methods=['GET'])
@requires_auth
def stop_alarm(identifier):
	a = Alarm.query.get_or_404(identifier)
	a.stop()
	return jsonify({'Status': 'OK'})


@alarm_blueprint.route('/add/detector', methods=['POST'])
@requires_auth
def add_detector():
	from detector import Detector
	data = request.get_json(force=True)
	a = Alarm.query.get_or_404(data.get('identifier'))
	a.detectors.append(Detector.query.get_or_404(data.get('detector')))
	db.session.add(a)
	db.session.commit()
	return json.dumps({'Status': 'OK'})


@alarm_blueprint.route('/remove/detector', methods=['POST'])
@requires_auth
def remove_detector():
	from detector import Detector
	data = request.get_json(force=True)
	a = Alarm.query.get_or_404(data.get('identifier'))
	d = Detector.query.get_or_404(data.get('detector'))
	if d in a.detectors:
		a.detectors.remove(d)
		db.session.add(a)
		db.session.commit()
	else:
		print "Detector not in list"
	return json.dumps({'Status': 'OK'})




