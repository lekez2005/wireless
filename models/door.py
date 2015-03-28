__author__ = 'lekez2005'

import sys, json
from flask import Blueprint, request
from device import Devices
from rfid import Rfid, Card
from encoder import Encoder


sys.path.insert(0, '../')
from app import db

class Door(db.Model):
	identifier = db.Column(db.String, primary_key=True)
	pretty_name = db.Column(db.String(50))
	device_type = db.Column(db.String(50), default=Devices.DOOR)
	description = db.Column(db.Text)

	rfid = db.relationship('Rfid', uselist=False, backref='door', lazy='select')
	active = db.Column(db.Boolean, default=True)

	def __init__(self, identifier, description, pretty_name=None):
		self.identifier = identifier
		self.description = description
		self.identifier = identifier
		self.description = description
		if pretty_name is None:
			self.pretty_name = identifier
		else:
			self.pretty_name = pretty_name

	def __repr__(self):
		return '<Door: %s>' % (self.pretty_name, )

	@classmethod
	def load_to_dict(cls, modules):
		try:
			doors = cls.query.all()
			if doors is not None:
				modules[Devices.DOOR] = []
				for d in doors:
					modules[Devices.DOOR].append((d.identifier, d.pretty_name))
		except Exception, e:
			print e

	def react(self):
		pass

	def unlock(self):
		print 'Unlock door'

	def lock(self):
		print 'Lock door'

class JsonEncoder(Encoder):
	def default(self, o):
		if not (isinstance(o, Rfid) or
                        isinstance(o, Card) or isinstance(o, Door)):
			return super(JsonEncoder, self).default(o)
		return o.__dict__

door_blueprint = Blueprint('door', __name__)

@door_blueprint.route('/<identifier>', methods=['GET'])
def get_door(identifier):
	d = Door.query.get_or_404(identifier)
	d.rfid
	return json.dumps(d, cls=JsonEncoder)


@door_blueprint.route('/unlock/<identifier>')
def unlock_door(identifier):
	d = Door.query.get_or_404(identifier)
	d.unlock()
	return json.dumps({'Status': 'OK'})

@door_blueprint.route('/lock/<identifier>')
def lock_door(identifier):
	d = Door.query.get_or_404(identifier)
	d.lock()
	return json.dumps({'Status': 'OK'})

@door_blueprint.route('/update', methods=['POST'])
def update_door():
	data = request.get_json(force=True)
	print data
	return json.dumps({'Status': 'OK'})
