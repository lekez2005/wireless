__author__ = 'lekez2005'

import json, encoder

class Devices:
	ALARM = "alarm"
	DETECTOR = "detector"
	RFID = "rfid"
	DOOR = "door"

def load_modules():
	modules = {}
	# load detectors from database
	from detector import Detector
	Detector.load_to_dict(modules)

	# load alarm from database
	from alarm import Alarm
	Alarm.load_to_dict(modules)

	# load rfid
	from rfid import Rfid
	Rfid.load_to_dict(modules)

	from door import Door
	Door.load_to_dict(modules)

	return modules