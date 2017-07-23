#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import threading
from PyQt4 import QtGui  # (the example applies equally well to PySide)
import pyqtgraph as pg
import numpy as np
from NeatoXV11 import XV11

#Globals
shutdown = False
app = QtGui.QApplication([''])
plot = None
lidar = None

def main():
	global plot
	w = QtGui.QWidget()
	plot = pg.PlotWidget()
	layout = QtGui.QGridLayout()
	w.setLayout(layout)
	layout.addWidget(plot, 0, 0)
	w.show()

	#t = threading.Thread(target=threadSerial, args=())
	#t.start()

	global XV11
	lidar = XV11()
	lidar.Connect()

	x = np.arange(1000)
	y = np.random.normal(size=(3, 1000))
	#plot = pg.plot(title="Three plot curves")
	for i in range(3):
		plot.plot(x, y[i], pen=(i,3))  ## setting pen=(i,3) automaticaly creates three different-colored pens

	#waitForExit()
	app.exec_()
	global shutdown
	shutdown = True
	lidar.Disconnect()

	sys.exit(0)

if __name__ == '__main__':
	main()

