__author__ = 'lekez2005'


import RPi.GPIO as GPIO
import time, threading

AUTH_PIN = 26
AUTH_INDICATOR = 19
lock = None

current_milli_time = lambda: int(round(time.time() * 1000))

def setup():
	global lock
	lock = threading.RLock()
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(AUTH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(AUTH_INDICATOR, GPIO.OUT)


def authorize(timeout=8000):
	acq = lock.acquire(False)
	if acq == False:
		return False
	start_time = current_milli_time()
	output = True
	while current_milli_time()-start_time < timeout:
		GPIO.output(AUTH_INDICATOR, output)
		if GPIO.input(AUTH_PIN) == 1:
			lock.release()
			return True
		time.sleep(0.1)
		output = not output
	lock.release()
	return False




def clean_up():
	GPIO.cleanup()



