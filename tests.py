__author__ = 'lekez2005'

from app import process_xbee
base = {'rf_data': 'rfid#frontdoor#6A 00 49 DF 8D \r\n', 'rssi': ',', 'source_addr': '\x00\x03', 'id': 'rx', 'options': '\x00'}

def test_detector():
	base['rf_data'] = 'detector#window1#Triggered'
	print base
	process_xbee(base)


test_detector()