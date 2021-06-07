from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
import platform
import sys
import os
import ok
import time
import h5py
import numpy as np
import json
import datetime

#local import, needed for the fpga initialization
from fpga import FPGA

#Initializing the start time of the program
#As well as the time and date for file naming
start_time= time.time()
now = datetime.datetime.now()
current_time = now.strftime("%H_%M_%S")

#I could put these into a dictionary/register map
pipe_address = 0xA1
trig_address = 0x60
trig_mask = 0x04

#Creating one instance of the fpga/one instance of frontpanel
f = FPGA()
f.init_device()
dev = ok.okCFrontPanel()
dev.OpenBySerial("")

#Placeholding array to hold the data the retention data 
data_set = [5,6]

#Function assigning the difference between start time and time elapsed
def x():
    return float((int((time.time()-start_time)*10))/10)

#Reads the data held in the fifo, chaged to 64kB of data
def fifo_read(): 
    buf,e  = f.read_pipe_out(pipe_address, 16384)
    return buf

#Connected to a "half-full" trigger to signal the read
def trig_check():
    dev.UpdateTriggerOuts()
    tf = dev.IsTriggered(trig_address, trig_mask)
    return tf

#meta data to be printed in the Json Post-run file 
def get_meta_data():
    meta_dict = {
        "time" : (str)(current_time),
        "Date" : "{:%d, %b %Y}".format(datetime.date.today()),
        "Device Version": dev.GetDeviceMajorVersion(),
        "Platform" : platform.system(),
        "Version" : platform.version()
    }
    return meta_dict

#This is to be changed, max voltage value allowed by the read
voltage_value = 4.09

def twos_comp(val, bits):

    def twos_comp_scalar(val, bits):
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val                         # return positive value as is

    if hasattr(val, "__len__"):
        tmp_arr = np.array([])
        for v in val:
            tmp_arr = np.append(tmp_arr, twos_comp_scalar(v,bits))
        return tmp_arr
    else:
        return twos_comp_scalar(val, bits)

def convert_data(buf):
    bits = 16 # for AD7961 bits=18 for AD7960
    d = np.frombuffer(buf, dtype=np.uint8).astype(np.uint32)
    if bits == 16:
        d2 = d[0::4] + (d[1::4] << 8)
    elif bits == 18:
        # not sure of this 
        d2 = (d[3::4]<<8) + d[1::4] + ((d[0::4]<<16) & 0x03)
        # d2 = (d[3::4]<<8) + d[1::4] + ((d[0::4]<<16) & 0x03)

    d_twos = twos_comp(d2, bits)
    return d_twos

def y():
  y = Arr_to_int(convert_data(fifo_read()))
  print (y*voltage_value/131072)
  return (y*voltage_value/131072)

def Arr_to_int(y):
  t=0
  for i in range (len(y)-1):
    t = t + y.item(i)
  return t

#Creates a file with a single dataset, named with time of day
def filemaker(d1):
    nom = ("OPAMPDATA" + (str)(current_time)+ ".hdf5")
    hf = h5py.File(nom, 'w')
    hf.create_dataset('dataset_1', data=data_set)
    hf.close()
    data=get_meta_data()
    with open ('metadata' + (str) (current_time) + ".json", 'w') as outfile:
        json.dump(data, outfile)
    hdf5_reader(nom)

#Temp way to read my HDF5 files without third party software 
def hdf5_reader(nom):
    hf = h5py.File(nom, 'r')
    print ("The data in the hdf5 file is: " + (str)(hf.keys()))

#Once save and exit is pushed, data is saved in a new CSV file        
def save_and_exit():
  print ("Saving and exiting the program")
  if (len(data_set)!=0):
    filemaker(data_set)
  sys.exit()

#If the "Run" button is pushed, the save and exit button will become an option
def main_loop():
    if (f.xem.NoError != f.xem.OpenBySerial("")):
            print ("You can't run the software if no device is detected")
            return(False)
    else:
        os.system('python Main.py')

#Linked to the "exit" button on the main window 
def ex():
    sys.exit()

#Qt5 window class, to be initializaed upon call to Main.py
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

    #Call to trig_check()  for interval, default is set to 0 ns
    def update_plot_data(self):
        if (trig_check()):
            self.x = self.x[1:]  # Remove the first y element.
            a=(self.x[-1] + 1)
            self.x.append(a)  # Add a new value 1 higher than the last.
            self.y = self.y[1:]  # Remove the first
            b=y()
            self.y.append(b)  # Add a new random value.
            data_set.append([b,a]) #appending to the evential CSV file
            self.data_line.setData(self.x, self.y)  # Update the data.

#This block creates the custom selection window 
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
window.setStyleSheet("background-color: grey")
window.setGeometry(500,200,500,200)
window.show()
