from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
import sys
import os
import ok
import time
import csv
import numpy as np
from datetime import datetime

#local imports, needing the fpga initialization
#and the AD7960 data from the driver to graph
from fpga import FPGA
from AD7960driver import y 

#Initializing the start time of the program
#As well as the time and date for file naming
start_time= time.time()
now = datetime.now()
current_time = now.strftime("%H_%M_%S")

#Placeholding array to hold the data the retention data 
data_set = []

#Function assigning the difference between start time and time elapsed
def x():
    return float((int((time.time()-start_time)*10))/10)

#Creates a file with a single dataset, named with time of day
def filemaker(d1):
    nom = ("OPAMPDATA" + (str)(current_time))

    with open((str)(nom), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(d1)

#Once save and exit is pushed, data is saved in a new CSV file        
def save_and_exit():
  print ("Saving and exiting the program")
  if (len(data_set)!=0):
    filemaker(data_set)
  sys.exit()

#If the "Run" button is pushed, the save and exit button will become an option
def main_loop():
    os.system('python Main.py')

#Linked to the "exit" button on the main window 
def ex():
    sys.exit()

#Qt5 window class, will graph locally instead of drawing from Matplotlib
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
        data_set.append(b) #appending to the evential CSV file
        self.data_line.setData(self.x, self.y)  # Update the data.

#The old contents of UI.py, makes the button window 
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle('OPAMP GUI')
layout = QVBoxLayout()

btn = QPushButton('Run software')
btn.clicked.connect(main_loop)
bt = QPushButton('Exit')
bt.clicked.connect(ex)  
b = QPushButton('Save and Exit')
b.clicked.connect(save_and_exit)
layout.addWidget(btn)
layout.addWidget(bt)
layout.addWidget(b)
msg = QLabel('')
layout.addWidget(msg)
window.setLayout(layout)
window.setStyleSheet("background-color: grey;")
window.setGeometry(500,200,500,200)
window.show()

#Creates one instance of the front panel
xem = ok.okCFrontPanel()

if (xem.NoError != xem.OpenBySerial("")):
    print ("The graphing will not commence due to an error")
    sys.exit()

else:
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
