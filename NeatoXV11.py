import serial
import time
import threading
import math
xv11Serial = None
shutdown = False

class AngleData:
	def __init__(self, degree, distance, quality, x, y):
		self.degree = degree
		self.quality = quality
		self.distance = distance
		self.x = x
		self.y = y
	def __repr__(self):
		return 'r: %d x: %d y: %d q: %d' % (self.distance, self.x, self.y, self.quality)

class XV11:
	speed = 0
	index = 0
	angles = [AngleData(0, 0, 0, 0, 0) for i in range(360)]
	x = [[] for i in range(360)]
	y = [[] for i in range(360)]
	init_level = 0
	nb_errors = 0
	def __init__(self, **kwargs):
		self.port = kwargs.get('port', '/dev/ttyUSB0')
		self.baud = kwargs.get('baud', 115200)
		self.offset = kwargs.get('offset', 0)

	def Connect(self):
		global shutdown
		shutdown = False
		#print('Connect')
		global xv11Serial
		xv11Serial = serial.Serial(self.port, self.baud)
		t = threading.Thread(target=threadSerial, args=([self]))
		t.start()

	def Disconnect(self):
		global shutdown
		shutdown = True
		#print('Disconnect')
		xv11Serial.close()

def threadSerial(self):
	while shutdown == False:
		time.sleep(0.00001)
		#print('Sleep ' + self.port)
		if self.init_level == 0 :
			b = ord(xv11Serial.read(1))
			# start byte
			if b == 0xFA :
				self.init_level = 1
			else:
				self.init_level = 0
		elif self.init_level == 1:
			# position index
			b = ord(xv11Serial.read(1))
			if b >= 0xA0 and b <= 0xF9 :
				index = b - 0xA0
				self.init_level = 2
			elif b != 0xFA:
				self.init_level = 0
		elif self.init_level == 2 :
			# speed
			b_speed = [ ord(b) for b in xv11Serial.read(2)]

			# data
			b_data0 = [ ord(b) for b in xv11Serial.read(4)]
			b_data1 = [ ord(b) for b in xv11Serial.read(4)]
			b_data2 = [ ord(b) for b in xv11Serial.read(4)]
			b_data3 = [ ord(b) for b in xv11Serial.read(4)]

			# for the checksum, we need all the data of the packet...
			# this could be collected in a more elegent fashion...
			all_data = [ 0xFA, index+0xA0 ] + b_speed + b_data0 + b_data1 + b_data2 + b_data3

			# checksum
			b_checksum = [ ord(b) for b in xv11Serial.read(2) ]
			incoming_checksum = int(b_checksum[0]) + (int(b_checksum[1]) << 8)

			# verify that the received checksum is equal to the one computed from the data
			self.index = index
			if checksum(all_data) == incoming_checksum:
				speed_rpm = compute_speed(b_speed) 
				self.speed = speed_rpm
				process_data(self, index * 4 + 0, b_data0)
				process_data(self, index * 4 + 1, b_data1)
				process_data(self, index * 4 + 2, b_data2)
				process_data(self, index * 4 + 3, b_data3)
			else:
				# the checksum does not match, something went wrong...
				self.nb_errors +=1
				# display the samples in an error state
				process_data(self, index * 4 + 0, [0, 0x80, 0, 0])
				process_data(self, index * 4 + 1, [0, 0x80, 0, 0])
				process_data(self, index * 4 + 2, [0, 0x80, 0, 0])
				process_data(self, index * 4 + 3, [0, 0x80, 0, 0])

			self.init_level = 0 # reset and wait for the next packet

		else: # default, should never happen...
			self.init_level = 0
	#print('Ending serial')

def compute_speed(data):
	speed_rpm = float( data[0] | (data[1] << 8) ) / 64.0
	return speed_rpm

def checksum(data):
	"""Compute and return the checksum as an int.
	data -- list of 20 bytes (as ints), in the order they arrived in.
	"""
	# group the data by word, little-endian
	data_list = []
	for t in range(10):
		data_list.append( data[2*t] + (data[2*t+1]<<8) )

	# compute the checksum on 32 bits
	chk32 = 0
	for d in data_list:
		chk32 = (chk32 << 1) + d

	# return a value wrapped around on 15bits, and truncated to still fit into 15 bits
	checksum = (chk32 & 0x7FFF) + ( chk32 >> 15 ) # wrap around to fit into 15 bits
	checksum = checksum & 0x7FFF # truncate to 15 bits
	return int( checksum )

def process_data(self, angle, data):
	"""Updates the view of a sample.
	Takes the angle (an int, from 0 to 359) and the list of four bytes of data in the order they arrived.
	"""
	#unpack data using the denomination used during the discussions
	x = data[0]
	x1= data[1]
	x2= data[2]
	x3= data[3]

	angle_rad = (360 - angle) * math.pi / 180.0
	c = math.cos(angle_rad)
	s = -math.sin(angle_rad)

	dist_mm = x | (( x1 & 0x3f) << 8) # distance is coded on 13 bits ? 14 bits ?
	quality = x2 | (x3 << 8) # quality is on 16 bits
	dist_x = dist_mm*c
	dist_y = dist_mm*s

	#print(angle)
	self.angles[angle] = AngleData(angle, dist_mm, quality, dist_x, dist_y)
	self.x[angle] = dist_x
	self.y[angle] = dist_y

