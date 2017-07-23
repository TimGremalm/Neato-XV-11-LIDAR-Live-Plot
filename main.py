#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import threading
from PyQt4 import QtGui  # (the example applies equally well to PySide)
import pyqtgraph as pg
import numpy as np
from NeatoXV11 import *

#Globals
shutdown = False
app = QtGui.QApplication([''])
plot = None
lidar = None
w = None

def main():
	global plot, w
	w = QtGui.QWidget()
	plot = pg.PlotWidget()
	layout = QtGui.QGridLayout()
	w.setLayout(layout)
	layout.addWidget(plot, 0, 0)
	w.show()

	global lidar
	lidar = XV11()
	lidar.Connect()

	#x = np.arange(1000)
	#y = np.random.normal(size=(3, 1000))
	#for i in range(3):
	#	plot.plot(x, y[i], pen=(i,3))  ## setting pen=(i,3) automaticaly creates three different-colored pens
	plot.setYRange(-6000, 6000)
	plot.setXRange(-6000, 6000)

	t = threading.Thread(target=plotLidar, args=())
	t.start()

	#waitForExit()
	app.exec_()
	global shutdown
	shutdown = True
	lidar.Disconnect()

	sys.exit(0)

def plotLidar():
	while shutdown == False:
		time.sleep(0.3)
		plot.clear()
		plot.plot(lidar.x, lidar.y, title="Three plot curves", symbol='o', symbolSize=8)
		w.setWindowTitle(str(lidar.speed))

if __name__ == '__main__':
	main()

