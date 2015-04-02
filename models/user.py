__author__ = 'lekez2005'
from alarm import Alarm
from flask import Blueprint, request, abort, jsonify
from authenticate import requires_auth

import sys
sys.path.insert(0, '../')
from app import db

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


user_blueprint = Blueprint('user', __name__)

def authorize():
	print "Implement hardware authorization here"
	return True

@user_blueprint.route('/users', methods=['GET'])
def get_users():
	users = User.query.all()
	user_dict = [{'authorized': user.authorized, 'name': user.name, 'identifier': user.identifier} for user in users]
	resp = {'Status': 'OK', 'users': user_dict}
	return jsonify(resp)

@user_blueprint.route('/register', methods=['POST'])
def register_user():
	data = request.get_json(force=True)
	identifier = data.get('identifier')
	if User.query.get(identifier) is not None:
		return jsonify({'Status': 'ERROR', 'error': "User already exists"})
	# implement hardware auhorization here
	if authorize():
		token = data.get('token')
		name = token
		try:
			name = data.get('name')
		except:
			pass
		u = User(identifier, token, name)
		u.authorized = True
		db.session.add(u)
		db.session.commit()
		return jsonify({'Status': 'OK'})
	else:
		abort(401)

@user_blueprint.route('/update/token', methods=['POST'])
def update_token():
	if not authorize():
		abort(401)
	data = request.get_json(force=True)
	identifier = data.get('identifier')
	u = User.query.get_or_404(identifier)
	token = data.get('token')
	u.token = token
	db.session.add(u)
	db.session.commit()
	return jsonify({'Status': 'OK'})

@user_blueprint.route('/update/gcm', methods=['POST'])
@requires_auth
def update_gcm():
	data = request.get_json(force=True)
	identifier = data.get('identifier')
	u = User.query.get_or_404(identifier)
	id = data.get('gcm_id')
	u.gcm_id = id
	db.session.add(u)
	db.session.commit()
	return jsonify({'Status': 'OK'})



@user_blueprint.route('/remove', methods=['POST'])
@requires_auth
def remove_user():
	data = request.get_json(force=True)
	identifier = data.get('identifier')
	u = User.query.get_or_404(identifier)
	db.session.delete(u)
	db.session.commit()
	return jsonify({'Status': 'OK'})

