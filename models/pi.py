__author__ = 'lekez2005'


import RPi.GPIO as GPIO
import time

AUTH_PIN = 26
AUTH_INDICATOR = 19

current_milli_time = lambda: int(round(time.time() * 1000))

def setup_pins():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(AUTH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(AUTH_INDICATOR, GPIO.OUT)


def authorize(timeout=5000):
	start_time = current_milli_time()
	output = True
	while current_milli_time-start_time < timeout:
		GPIO.output(AUTH_INDICATOR, output)
		if GPIO.input(AUTH_PIN) == 1:
			return True
		time.sleep(0.1)
		output = not output
	return False




def clean_up():
	GPIO.cleanup()


setup_pins()
authorize()
clean_up()

