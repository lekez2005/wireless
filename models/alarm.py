__author__ = 'lekez2005'

from flask import Blueprint, request, jsonify
from authenticate import requires_auth
import json
import pi

import sys

sys.path.insert(0, '../')
from app import db

from device import Devices
from encoder import Encoder

#db = SQLAlchemy()

IDENTIFIER = 'identifier'
PRETTY_NAME = 'pretty_name'
DESCRIPTION = 'description'
ADDRESS = 'address'
ACTIVE = 'active'


class Alarm(db.Model):
	identifier = db.Column(db.String(50), primary_key=True)
	pretty_name = db.Column(db.String(50))
	device_type = db.Column(db.String(50), default=Devices.ALARM)
	description = db.Column(db.Text)
	active = db.Column(db.Boolean, default=True)
	address = db.Column(db.Integer)

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

	def get_pi(self):
		if self.identifier == 'led1':
			return pi.a_one
		elif self.identifier == 'led2':
			return pi.a_two

	def ring(self, force=False):
		if self.active or force:
			if self.get_pi() is not None:
				self.get_pi().ring()

	def stop(self):
		if self.get_pi() is not None:
			self.get_pi().stop_ring()


class JsonEncoder(Encoder):
	def default(self, o):
		if not isinstance(o, Alarm):
			return super(JsonEncoder, self).default(o)
		return o.__dict__


def add_commit(item):
	try:
		db.session.add(item)
		db.session.commit()
	except Exception, e:
		print e.message
		db.session.rollback()

alarm_blueprint = Blueprint('alarm', __name__)

@alarm_blueprint.route('/', methods=['GET'])
@requires_auth
def get_all():
	all = Alarm.query.all()
	resp = {}

	resp['alarms'] = [{IDENTIFIER:a.identifier,
			 PRETTY_NAME: a.pretty_name,
			 DESCRIPTION: a.description,
			 ACTIVE: a.active} for a in all]
	resp['Status'] = 'OK'
	return jsonify(resp)

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
def update_alarm():
	data = request.get_json(force=True)
	al = Alarm.query.get_or_404(data.get('identifier'))
	if data.get('pretty_name') is not None:
		al.pretty_name = data.get('pretty_name')
	if data.get('active') is not None:
		al.active = data.get('active')
	if data.get('description') is not None:
		al.description = data.get('description')
	if data.get('address') is not None:
		al.address = data.get('address')
	add_commit(al)
	return jsonify({'Status': 'OK'})

@alarm_blueprint.route('/ring/<identifier>', methods=['GET'])
@requires_auth
def ring_alarm(identifier):
	a = Alarm.query.get_or_404(identifier)
	a.ring(True)
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
	add_commit(a)
	return jsonify({'Status': 'OK'})


@alarm_blueprint.route('/remove/detector', methods=['POST'])
@requires_auth
def remove_detector():
	from detector import Detector
	data = request.get_json(force=True)
	a = Alarm.query.get_or_404(data.get('identifier'))
	d = Detector.query.get_or_404(data.get('detector'))
	if d in a.detectors:
		a.detectors.remove(d)
		add_commit(a)
	else:
		print "Detector not in list"
	return json.dumps({'Status': 'OK'})




