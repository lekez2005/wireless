__author__ = 'lekez2005'

import sys
sys.path.insert(0, '../')

from app import db


def init_db():
	from detector import Detector
	from alarm import Alarm
	#from rfid import Rfid, Card
	db.create_all()
	db.session.commit()
	print db.metadata.tables.keys()

def delete_all():
	from detector import Detector
	from alarm import Alarm
	#from rfid import Rfid, Card
	db.drop_all()
	db.session.commit()
	print db.metadata.tables.keys()

def init_detector():
	from detector import Detector
	d1 = Detector("frontdoor", "Front Door", "Knock detector")
	db.session.add(d1)
	db.session.commit()
	print Detector.query.all()

def init_cards():
	from rfid import Rfid, Card
	db.drop_all()
	db.create_all()
	rf1 = Rfid('frontdoor', 'For front door', "Front Door")
	c1 = Card('6A0049DC', 'card 1', 'Card 1')
	c1.rfid_identifier = rf1.identifier
	c2 = Card('6A0049DF', 'card 2', 'Card 2')
	c2.rfid_identifier = rf1.identifier
	db.session.add(rf1)
	db.session.add(c1)
	db.session.add(c2)
	db.session.commit()



def init_alarm():
	from alarm import Alarm
	a1 = Alarm("alarm1", "Loud speaker", "Alarm 1")
	db.session.add(a1)
	db.session.commit()
	print Alarm.query.all()

def reinitialize():
	delete_all()
	init_db()
	init_detector()
	init_alarm()
	init_cards()

#reinitialize()
#init_db()
#init_detector()
#init_alarm()
#reinitialize()
#init_cards()

from door import Door
from rfid import Rfid, Card
from alarm import Alarm
from detector import Detector
from user import User, alarms
u = User.query.first()
#ds = Detector.query.all()
#for d in ds:
#	print d.identifier
# print d
# u.detectors.append(d)
# db.session.add(u)
# db.session.commit()
d = Detector.query.get('frontdoor')
u.detectors.append(d)
db.session.add(u)
db.session.commit()
print u.gcm_id

