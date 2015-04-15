__author__ = 'lekez2005'

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from encoder import Encoder
import json, datetime
import sys
sys.path.insert(0, '../')
from app import db
from authenticate import requires_auth

from device import Devices

class Rfid(db.Model):
	identifier = db.Column(db.String(50), primary_key=True)
	pretty_name = db.Column(db.String(50))
	device_type = db.Column(db.String(50), default=Devices.RFID)
	description = db.Column(db.Text)
	door_identifier = db.Column(db.String, db.ForeignKey('door.identifier'))
	cards = db.relationship('Card', backref='rfid', lazy='select')
	active = db.Column(db.Boolean, default=True)
	address = db.Column(db.Integer)

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
		return '<RFID: %s>' % (self.pretty_name, )

	def react(self, message):
		from door import Door
		print message
		mess = "".join((message.split())[0:4])
		print 'Attempted login with id ' + mess
		id = Card.query.get(mess)
		if id is not None:
			if id.valid:
				self.door.unlock()
			else:
				pass #TODO signal invalid id here
		else:

			c = Card(mess, datetime.datetime.now().strftime("Added %a, %b %d %Y %H:%M"))
			c.rfid_identifier = self.identifier
			db.session.add(c)
			db.session.commit()
			print "Added new card " + mess

	@classmethod
	def load_to_dict(cls, modules):
		try:
			rfids = cls.query.all()
			if rfids is not None:
				modules[Devices.RFID] = []
				for rf in rfids:
					modules[Devices.RFID].append((rf.identifier, rf.pretty_name))
		except Exception, e:
			print e


class Card(db.Model):
	identifier = db.Column(db.String(50), primary_key=True)
	pretty_name = db.Column(db.String(50))
	valid = db.Column(db.Boolean, default=True)
	description = db.Column(db.Text)
	rfid_identifier = db.Column(db.String, db.ForeignKey('rfid.identifier'))

	def __init__(self, identifier, description, pretty_name=None):
		self.identifier = identifier
		self.description = description
		if pretty_name is None:
			self.pretty_name = identifier
		else:
			self.pretty_name = pretty_name


	def __repr__(self):
		return '<Card: %s>' % (self.pretty_name, )



rfid = Blueprint('rfid', __name__)

class JsonEncoder(Encoder):
	def default(self, o):
		if not (isinstance(o, Rfid) or isinstance(o, Card)):
			return super(JsonEncoder, self).default(o)
		return o.__dict__


@rfid.route('/<identifier>', methods=['GET'])
@requires_auth
def get_rfid(identifier):
	rf = Rfid.query.get_or_404(identifier)
	rf.cards
	return json.dumps(rf, cls=JsonEncoder)

@rfid.route('/remove/<card_identifier>', methods=['GET'])
@requires_auth
def delete_card(card_identifier):
	card = Card.query.get_or_404(card_identifier)
	db.session.delete(card)
	db.session.commit()
	return json.dumps({'Status': 'OK'})

@rfid.route('/enable/<card_identifier>', methods=['GET', 'POST'])
@requires_auth
def enable_card(card_identifier):
	card = Card.query.get_or_404(card_identifier)
	card.valid = True
	try:
		db.session.add(card)
		db.session.commit()
		return json.dumps({'Status': 'OK'})
	except:
		db.session.rollback()
		return json.dumps({'Status': 'Error', 'error': 'Database error'})


@rfid.route('/update', methods=['POST'])
@requires_auth
def update_card():
	data = request.get_json(force=True)
	c = Card.query.get_or_404(data.get('identifier'))
	c.pretty_name = data.get('pretty_name')
	c.valid = data.get('valid')
	c.description = data.get('description')
	db.session.add(c)
	db.session.commit()
	return json.dumps({'Status': 'OK'})


@rfid.route('/disable/<card_identifier>', methods=['GET', 'POST'])
@requires_auth
def disable_card(card_identifier):
	card = Card.query.get_or_404(card_identifier)
	card.valid = False
	try:
		db.session.add(card)
		db.session.commit()
		return json.dumps({'Status': 'OK'})
	except:
		db.session.rollback()
		return json.dumps({'Status': 'Error', 'error': 'Database error'})

@rfid.route('/<identifier>/add', methods=['POST'])
@requires_auth
def add_card(identifier):
	rf = Rfid.query.get_or_404(identifier)
	data = request.get_json(force=True)
	print data
	try:
		id = data.get('identifier')
		desc, pretty = (None, None)
		if 'description' in data:
			desc = data.get('description')
		if 'pretty_name' in data:
			pretty = data.get('pretty_name')
		if desc is None:
			desc = id
		card = Card(id, desc, pretty)
		card.rfid_identifier = identifier
		db.session.add(card)
		db.session.commit()
		return json.dumps(Card.query.get(id), cls=JsonEncoder)
	except IntegrityError, e:
		print e
		db.session.rollback()
		return json.dumps({'Status': 'Error', 'error': 'Card Already exists'})
	except Exception, e:
		print e
		return json.dumps({'Status': 'Error', 'error': 'Bad request'})




