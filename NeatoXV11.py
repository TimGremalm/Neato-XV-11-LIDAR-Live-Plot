import serial
import time
import threading
xv11Serial = None
shutdown = False
class XV11:
	speed = 0
	data = []
	#xv11Serial.close()
	def __init__(self, **kwargs):
		self.port = kwargs.get('port', '/dev/ttyUSB0')
		self.baud = kwargs.get('baud', 115200)
		self.offset = kwargs.get('offset', 0)

	def Connect(self):
		global shutdown
		shutdown = False
		print('Connect')
		#xv11Serial = serial.Serial(xv11Port, xv11Baud)
		t = threading.Thread(target=threadSerial, args=([self]))
		t.start()

	def Disconnect(self):
		global shutdown
		shutdown = True
		print('Disconnect')

def threadSerial(self):
	while shutdown == False:
		print('Sleep ' + self.port)
		time.sleep(1)
	print('Ending serial')

