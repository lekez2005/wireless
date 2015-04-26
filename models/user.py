__author__ = 'lekez2005'
import pi
from alarm import Alarm
from detector import Detector
from flask import Blueprint, request, abort, jsonify
from authenticate import requires_auth
from gcm import GCM

import sys

sys.path.insert(0, '../')
from app import db

detectors = db.Table('user_detector',
					 db.Column('detector_id', db.String, db.ForeignKey('detector.identifier')),
					 db.Column('user_id', db.String, db.ForeignKey('user.identifier'))
					 )

alarms = db.Table('user_alarm',
				  db.Column('alarm_id', db.String, db.ForeignKey('alarm.identifier')),
				  db.Column('user_id', db.String, db.ForeignKey('user.identifier'))
				  )


class User(db.Model):
	identifier = db.Column(db.String, primary_key=True)
	token = db.Column(db.String, nullable=False)
	name = db.Column(db.String)
	authorized = db.Column(db.Boolean, default=False)
	gcm_id = db.Column(db.String)
	notify = db.Column(db.Boolean, default=False)

	detectors = db.relationship(Detector, secondary=detectors,
								backref=db.backref('users', lazy='select'))

	alarms = db.relationship(Alarm, secondary=alarms,
							 backref=db.backref('users', lazy='select'))

	def __init__(self, identifier, token, name=None):
		self.identifier = identifier
		self.token = token
		if name is None:
			self.name = identifier
		else:
			self.name = name

	def __repr__(self):
		return '<User: %s>' % self.name


def add_commit(item):
	try:
		db.session.add(item)
		db.session.commit()
	except Exception, e:
		print e.message
		db.session.rollback()


user_blueprint = Blueprint('user', __name__)


def authorize():
	return pi.authorize(8000)


@user_blueprint.route('/users', methods=['GET'])
def get_users():
	users = User.query.all()
	user_dict = [{'authorized': user.authorized, 'name': user.name, 'identifier': user.identifier} for user in users]
	resp = {'Status': 'OK', 'users': user_dict}
	return jsonify(resp)


@user_blueprint.route('/user/<identifier>')
@requires_auth
def get_user(identifier):
	u = User.query.get_or_404(identifier)
	resp = {'Status': 'OK', 'user': {'identifier': u.identifier, 'name': u.name,
			'authorized': u.authorized, 'notify': u.notify}}
	return jsonify(resp)


@user_blueprint.route('/register', methods=['POST'])
def register_user():
	data = request.get_json(force=True)
	identifier = data.get('identifier')
	if User.query.get(identifier) is not None:
		return jsonify({'Status': 'ERROR', 'error': "User already exists"})
	if not identifier:
		return jsonify({'Status': 'ERROR', 'error': "Empty user identifier"})
	# implement hardware auhorization here
	if authorize():
		token = data.get('token')  # TODO remove this requirement
		name = token
		try:
			name = data.get('name')
		except:
			pass

		u = User(identifier, token, name)
		u.authorized = True
		u.notify = True
		try:
			db.session.add(u)
			db.session.commit()
			return jsonify({'Status': 'OK'})
		except:
			db.session.rollback()
			return jsonify({'Status': 'ERROR', 'error': "User already exists"})
	else:
		return jsonify({'Status': 'ERROR', 'error': 'Not authorized'})


@user_blueprint.route('/update/token', methods=['POST'])
def update_token():
	if not authorize():
		abort(401)
	userid = request.headers['user_id']
	u = User.query.get(userid)
	u.token = ""
	u.gcm_id = None
	add_commit(u)
	print "Old record purged"

	data = request.get_json(force=True)
	identifier = data.get('identifier')
	u = User.query.get_or_404(identifier)
	token = data.get('token')
	u.token = token
	id = data.get('gcm_id')
	u.gcm_id = id
	add_commit(u)
	return jsonify({'Status': 'OK'})


@user_blueprint.route('/edit', methods=['POST'])
@requires_auth
def edit_user():
	data = request.get_json(force=True)
	identifier = data.get('identifier')
	u = User.query.get_or_404(identifier)
	u.name = data.get('name')
	u.authorized = data.get('authorized')
	u.notify = data.get('notify')
	try:
		db.session.add(u)
		db.session.commit()
		return jsonify({'Status': 'OK'})
	except Exception, e:
		db.session.rollback()
		return jsonify({'Status': 'ERROR', 'error': e.message})


@user_blueprint.route('/update/gcm', methods=['POST'])
@requires_auth
def update_gcm():
	data = request.get_json(force=True)
	identifier = data.get('identifier')
	u = User.query.get_or_404(identifier)
	id = data.get('gcm_id')
	u.gcm_id = id
	add_commit(u)
	return jsonify({'Status': 'OK'})


@user_blueprint.route('/delete/<identifier>', methods=['GET'])
@requires_auth
def remove_user(identifier):
	u = User.query.get_or_404(identifier)
	try:
		db.session.delete(u)
		db.session.commit()
		return jsonify({'Status': 'OK'})
	except Exception, e:
		db.session.rollback
		return jsonify({'Status': 'ERROR', 'error': e.message})



class GcmMessage():
	# TODO move to config
	API_KEY = 'AIzaSyDMZKT9sArFwBI8k2TAm-0FNgU37ulegWU'
	gcm = GCM(API_KEY)


	@classmethod
	def send_mesage(cls, ids, data):
		response = cls.gcm.json_request(registration_ids=ids, data=data)

		if 'errors' in response:
			for error, reg_ids in response['errors'].items():
				if error in ['NotRegistered', 'InvalidRegistration']:
					for reg_id in reg_ids:
						u = User.query.filter(gcm_id=reg_id).first()
						u.gcm_id = None
						add_commit(u)
		if 'canonical' in response:
			for reg_id, canonical_id in response['canonical'].items():
				u = User.query.filter(gcm_id=reg_id).first()
				u.gcm_id = canonical_id
				add_commit(u)




