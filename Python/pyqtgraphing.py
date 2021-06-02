from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import ok
from random import randint
import time
from fpga import FPGA
from AD7960driver import y 
from CSVfilemaker import filemaker

#Initializing the start time of the program
start_time= time.time()
d1 = []

#Function assigning the difference between start time and time elapsed
def x():
    return float((int((time.time()-start_time)*10))/10)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))  # 100 time points
        self.y = [y() for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):

        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        b=y()
        self.y.append(b)  # Add a new random value.
        d1.append(b) #appending to the evential CSV file

        self.data_line.setData(self.x, self.y)  # Update the data.

xem = ok.okCFrontPanel()
if (xem.NoError != xem.OpenBySerial("")):
    print ("The graphing will not commence due to an error")

else:
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

filemaker(d1)
