__author__ = 'lekez2005'

import sys, json
from flask import Blueprint, request, jsonify
from authenticate import requires_auth
from device import Devices
from rfid import Rfid, Card
from encoder import Encoder


sys.path.insert(0, '../')
from app import db, transmit_message

IDENTIFIER = 'identifier'
PRETTY_NAME = 'pretty_name'
DESCRIPTION = 'description'
ADDRESS = 'address'
ACTIVE = 'active'


class Door(db.Model):
	identifier = db.Column(db.String, primary_key=True)
	pretty_name = db.Column(db.String(50))
	device_type = db.Column(db.String(50), default=Devices.DOOR)
	description = db.Column(db.Text)

	rfid = db.relationship('Rfid', uselist=False, backref='door', lazy='select')
	active = db.Column(db.Boolean, default=True)
	address = db.Column(db.Integer)

	def __init__(self, identifier, description, address, pretty_name=None, active=True):
		self.identifier = identifier
		self.description = description
		self.address = address
		self.identifier = identifier
		self.description = description
		self.active = active
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
					do = {IDENTIFIER: d.identifier, PRETTY_NAME: d.pretty_name,
						  DESCRIPTION:d.description, ADDRESS: d.address,
						  ACTIVE: d.active}
					modules[Devices.DOOR].append(do)
		except Exception, e:
			print e

	def react(self):
		pass

	def unlock(self):
		if self.address is not None:
			transmit_message(self.address, Devices.DOOR + "#%s#unlock"%self.identifier)
			return True
		return False

	def lock(self):
		if self.address is not None:
			transmit_message(self.address, Devices.DOOR + "#%s#lock"%self.identifier)
			return True
		else:
			return False

class JsonEncoder(Encoder):
	def default(self, o):
		if not (isinstance(o, Rfid) or
                        isinstance(o, Card) or isinstance(o, Door)):
			return super(JsonEncoder, self).default(o)
		return o.__dict__

door_blueprint = Blueprint('door', __name__)

@requires_auth
@door_blueprint.route('/add', methods=['POST'])
def add_door():
	data = request.get_json(force=True)
	id = data.get('identifier')
	d = {}
	d['description'] = data.get('description')
	d['address'] = data.get('address')
	if 'pretty_name' in data:
		d['pretty_name'] = data.get('pretty_name')
	if 'active' in data:
		d['active'] = data.get('active')
	do = Door(id, d['description'], d['address'], pretty_name=d['pretty_name'], active=d['active'])
	print do
	db.session.add(do)
	db.session.commit()
	return jsonify({'Status': 'OK'})

@door_blueprint.route('/<identifier>', methods=['GET'])
@requires_auth
def get_door(identifier):
	d = Door.query.get_or_404(identifier)
	d.rfid
	resp = json.loads(json.dumps(d, cls=JsonEncoder))
	resp['Status'] = 'OK'
	return jsonify(resp)


@door_blueprint.route('/unlock/<identifier>')
@requires_auth
def unlock_door(identifier):
	d = Door.query.get_or_404(identifier)
	if d.unlock():
		return jsonify({'Status': 'OK'})
	return jsonify({'Status': 'ERROR', 'error': 'No address'})

@door_blueprint.route('/lock/<identifier>')
@requires_auth
def lock_door(identifier):
	d = Door.query.get_or_404(identifier)
	if d.lock():
		return jsonify({'Status': 'OK'})
	return jsonify({'Status': 'ERROR', 'error': 'No address'})

@door_blueprint.route('/update', methods=['POST'])
@requires_auth
def update_door():
	data = request.get_json(force=True)
	id = data.get('identifier')
	d = Door.query.get_or_404(id)
	if 'description' in data:
		d.description = data.get('description')
	if 'pretty_name' in data:
		d.pretty_name = data.get('pretty_name')
	if 'address' in data:
		d.address = data.get('address')
	if 'active' in data:
		d.active = data.get('active')
	if 'rfid' in data:
		try:
			rf = Rfid.query.get(data.get('rfid'))
			d.rfid = rf
		except Exception:
			pass
	db.session.add(d)
	db.session.commit()
	return jsonify({'Status': 'OK'})
