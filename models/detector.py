__author__ = 'lekez2005'

from flask import Blueprint, request, jsonify
from authenticate import requires_auth
import json


import sys
sys.path.insert(0, '../')
from app import db

from encoder import Encoder
from device import Devices
from alarm import Alarm


IDENTIFIER = 'identifier'
PRETTY_NAME = 'pretty_name'
DESCRIPTION = 'description'
ADDRESS = 'address'
ACTIVE = 'active'
ALARMS = 'alarms'
ALARM_MESSAGE = 'alarm_message'

alarms = db.Table('detector_alarm',
					 db.Column('alarm_id', db.String, db.ForeignKey('alarm.identifier')),
					 db.Column('detector_id', db.String, db.ForeignKey('detector.identifier'))
)


class Detector(db.Model):
	identifier = db.Column(db.String(50), primary_key=True)
	pretty_name = db.Column(db.String(50))
	device_type = db.Column(db.String(50), default=Devices.DETECTOR)
	description = db.Column(db.Text)
	active = db.Column(db.Boolean, default=True)
	alarms = db.relationship(Alarm, secondary=alarms,
							 backref=db.backref('detectors', lazy='select'))
	alarm_message = db.Column(db.Text)
	address = db.Column(db.Integer)

	def __init__(self, identifier, description, pretty_name=None, alert_m = None):
		self.identifier = identifier
		self.description = description
		if pretty_name is None:
			self.pretty_name = identifier
		else:
			self.pretty_name = pretty_name

		if alert_m is not None:
			self.alarm_message = alert_m
		else:
			self.alarm_message = 'Detector %s triggered' % identifier

	@classmethod
	def load_to_dict(cls, modules):
		try:
			detectors = cls.query.filter_by(active=True).all()
			if detectors is not None:
				modules[Devices.DETECTOR] = []
				for det in detectors:
					modules[Devices.DETECTOR].append((det.identifier, det.pretty_name))
		except Exception, e:
			print e




	def __repr__(self):
		return '<Detector: %s, %s>' % (self.identifier, self.description)

	def react(self, message):

		if self.active:
			if message != 'Stop':
				self.notify_users()
				for al in self.alarms:
					al.ring()
			else:
				for al in self.alarms:
					al.stop()

		print "React to " + message

	def notify_users(self):
		from user import User, detectors, GcmMessage
		users = User.query.all()
		gcm_ids = []
		for u in users:
			print u
			if u.notify and u.gcm_id:
				gcm_ids.append(u.gcm_id)
		if gcm_ids:
			mess = {'device': self.device_type, 'identifier': self.identifier, 'message': self.alarm_message}
			print 'Sending message' + str(mess)
			GcmMessage.send_mesage(gcm_ids, mess)

	def respond_to_app(self, app_message):
		pass

	def send_alarm(self):
		# get all configured alarms
		pass


class JsonEncoder(Encoder):
	def default(self, o):
		if not isinstance(o, Detector):
			return super(JsonEncoder, self).default(o)
		return o.__dict__

def add_commit(item):
	try:
		db.session.add(item)
		db.session.commit()
	except Exception, e:
		print e.message
		db.session.rollback()

detector_blueprint = Blueprint('detector', __name__)

@detector_blueprint.route('/', methods=['GET'])
@requires_auth
def get_all():
	all = Detector.query.all()
	resp = {}
	resp['detectors'] = [{IDENTIFIER: d.identifier,
						  PRETTY_NAME: d.pretty_name,
						  DESCRIPTION: d.description,
						  ACTIVE: d.active,
						  ADDRESS: d.address}
						 for d in all]
	resp['Status'] = 'OK'
	return jsonify(resp)

@detector_blueprint.route('/<identifier>', methods=['GET'])
@requires_auth
def get_detector(identifier):
	d = Detector.query.get_or_404(identifier)
	resp = json.loads(json.dumps(d, cls=JsonEncoder))
	resp['Status'] = 'OK'
	resp['alarms'] = [ [al.identifier, al.pretty_name]  for al in d.alarms]
	return jsonify(resp)

@detector_blueprint.route('/update', methods=['POST'])
@requires_auth
def update_detector():
	data = request.get_json(force=True)
	det = Detector.query.get_or_404(data.get(IDENTIFIER))
	if data.get(PRETTY_NAME) is not None:
		det.pretty_name = data.get(PRETTY_NAME)
	if data.get(ACTIVE) is not None:
		det.active = data.get(ACTIVE)
	if data.get(DESCRIPTION) is not None:
		det.description = data.get(DESCRIPTION)
	if data.get(ADDRESS) is not None:
		det.address = data.get(ADDRESS)
	if data.get(ALARM_MESSAGE) is not None:
		det.address = data.get(ALARM_MESSAGE)
	add_commit(det)
	return jsonify({'Status': 'OK'})


@detector_blueprint.route('/add/alarm', methods=['POST'])
@requires_auth
def add_alarm():
	data = request.get_json(force=True)
	det = Detector.query.get_or_404(data.get(IDENTIFIER))
	det.alarms.append(Alarm.query.get_or_404(data.get('alarm')))
	add_commit(det)
	return jsonify({'Status': 'OK'})

@detector_blueprint.route('/remove/alarm', methods=['POST'])
@requires_auth
def remove_alarm():
	data = request.get_json(force=True)
	det = Detector.query.get_or_404(data.get(IDENTIFIER))
	al = Alarm.query.get_or_404(data.get('alarm'))
	if al in det.alarms:
		det.alarms.remove(al)
		add_commit(det)
	else:
		print 'Alarm not in list'
	return jsonify({'Status': 'OK'})