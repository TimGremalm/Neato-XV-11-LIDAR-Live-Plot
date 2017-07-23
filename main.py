#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import threading
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4 import QtGui
from PyQt4.QtOpenGL import *
import math

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
	plot = OpenGLPlotWidget(plot)
	layout = QtGui.QGridLayout()
	w.setLayout(layout)
	layout.addWidget(plot, 0, 0)
	w.show()

	global lidar
	lidar = XV11()
	lidar.Connect()

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
		time.sleep(1)
		w.setWindowTitle(str(lidar.speed))

class OpenGLPlotWidget(QGLWidget):
	def __init__(self, parent):
		QGLWidget.__init__(self, parent)
		self.setMinimumSize(500, 500)

	def paintGL(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glLoadIdentity()

		# Draw in 'immediate mode'
		glColor(0.0, 1.0, 0.0)
		glBegin(GL_LINE_STRIP)
		for deg in lidar.angles:
			glVertex(deg.x, deg.y, 0.0)
		glEnd()

		glFlush()

	def resizeGL(self, w, h):
		glViewport(0, 0, w, h)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(40.0, 1.0, 1.0, 30.0)

	def initializeGL(self):
		# set viewing projection
		glClearColor(0.0, 0.0, 0.0, 1.0)
		glClearDepth(1.0)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(40.0, 1.0, 1.0, 30.0)

if __name__ == '__main__':
	main()

