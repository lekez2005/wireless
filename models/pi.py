__author__ = 'lekez2005'


import RPi.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
import time, datetime, threading

AUTH_PIN = 26
AUTH_INDICATOR = 19

ALARM_TOGGLE = 13
ALARM_INDICATOR = 6
ALARM_ACTIVE = True
RING_STOP = 5

ALARM_ONE = 22
ALARM_TWO = 27

current_milli_time = lambda: int(round(time.time() * 1000))

class Alarm:
	def __init__(self, pin):
		GPIO.setup(pin, GPIO.OUT)
		self.pin = pin
		self.lock = threading.RLock()
		#self.lock = threading.Lock()
		self.ringCondition = False
		self.count = 0
		self.timeout = float('inf')
		self.lastAlarm = current_milli_time()
		self.reason = None

	def pulse(self):
		acq = self.lock.acquire(False)
		if acq is False:
			return
		try:
			while self.ringCondition and current_milli_time() < self.lastAlarm + self.timeout:
				GPIO.output(self.pin, True)
				time.sleep(1)
				GPIO.output(self.pin, False)
				time.sleep(1)
			self.count = 0
			GPIO.output(self.pin, False)
		finally:
			self.lock.release()

	def ring(self, timeout=None, reason = None):
		'''
		timeout in milliseconds
		'''
		self.lastAlarm = current_milli_time()
		if timeout is not None:
			self.timeout = int(timeout)
		self.reason = reason
		self.count += 1
		self.ringCondition = True
		t = threading.Thread(target=self.pulse)
		t.setDaemon(True)
		t.start()



	def stop_ring(self, reason = None):
		if self.reason == reason:
			self.ringCondition = False





lock = None
a_one = None
a_two = None

lcd = None


def is_activated():
	return ALARM_ACTIVE

def alarm_toggle(channel):
	set_alarm_active(not ALARM_ACTIVE)

def stop_alarms(channel):
	a_one.stop_ring()
	a_two.stop_ring()
	display('Alarms Stopped', 2)


def setup():
	global lock, lcd, a_one, a_two

	lock = threading.RLock()
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(AUTH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(AUTH_INDICATOR, GPIO.OUT)
	GPIO.output(AUTH_INDICATOR, False)

	GPIO.setup(RING_STOP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(RING_STOP, GPIO.RISING, callback=stop_alarms, bouncetime=300)

	GPIO.setup(ALARM_INDICATOR, GPIO.OUT)
	GPIO.output(ALARM_INDICATOR, ALARM_ACTIVE)
	GPIO.setup(ALARM_TOGGLE, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(ALARM_TOGGLE, GPIO.RISING, callback=alarm_toggle, bouncetime=300)



	a_one = Alarm(22)
	a_two = Alarm(27)

	lcd = Adafruit_CharLCD(pins_db=[23, 16, 21, 12], GPIO=GPIO)
	lcd.begin(16, 2)


def set_alarm_active(state):
	global ALARM_ACTIVE
	ALARM_ACTIVE = state
	if state:
		display('Armed', 2)
	else:
		display('Disarmed', 2)
	GPIO.output(ALARM_INDICATOR, ALARM_ACTIVE)



def display(string, line=1):
	string = string[0:16]
	if line == 1:
		lcd.setCursor(0, 0)
		lcd.message(' '*16)
		lcd.setCursor(0, 0)
		lcd.message(string)
	else:
		lcd.setCursor(0, 1)
		lcd.message(' '*16)
		lcd.setCursor(0, 1)
		lcd.message(string)


def authorize(timeout=8000):
	acq = lock.acquire(False)
	if acq is False:
		return False
	start_time = current_milli_time()
	output = True
	while current_milli_time()-start_time < timeout:
		GPIO.output(AUTH_INDICATOR, output)
		if GPIO.input(AUTH_PIN) == 1:
			GPIO.output(AUTH_INDICATOR, False)
			lock.release()
			return True
		time.sleep(0.1)
		output = not output
	GPIO.output(AUTH_INDICATOR, False)
	lock.release()
	return False




def clean_up():
	GPIO.cleanup()



