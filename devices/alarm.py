__author__ = 'lekez2005'

import sys

sys.path.insert(0, '../')
from app import db

from device import Devices
from detector import Detector

#db = SQLAlchemy()

detectors = db.Table('device-alarm',
					 db.Column('alarm-id', db.String, db.ForeignKey('alarm.identifier')),
					 db.Column('detector-id', db.String, db.ForeignKey('detector.identifier'))
)


class Alarm(db.Model):
	identifier = db.Column(db.String(50), primary_key=True)
	pretty_name = db.Column(db.String(50))
	device_type = db.Column(db.String(50), default=Devices.ALARM)
	description = db.Column(db.Text)
	active = db.Column(db.Boolean, default=True)
	detectors = db.relationship(Detector, secondary=detectors,
								backref=db.backref('alarms', lazy='select'))


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

	def respond_to_app(self, app_message):
		pass


