__author__ = 'lekez2005'

from flask import Blueprint, request


import sys
sys.path.insert(0, '../')
from app import db

from device import Devices
from alarm import Alarm


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
		pass

	def respond_to_app(self, app_message):
		pass

	def send_alarm(self):
		# get all configured alarms
		pass


detector_blueprint = Blueprint('detector', __name__)

@detector_blueprint.route('alarms/<identifier>', methods=['GET'])
def get_alarms(identifier):
	pass

@detector_blueprint.route('alarms/add/<identifier>', methods=['POST'])
def add_alarm(identifier):
	pass

@detector_blueprint.route('alarms/remove/<identifier>', methods=['POST'])
def remove_alarm(identifier):
	pass