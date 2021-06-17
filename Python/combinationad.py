from PyQt5 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
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
from collections import namedtuple
import sys
from fpga import FPGA
import pickle as pkl 
from scipy import signal

#Local imports, full of pin locations
from create_source import adc_list


voltage_value = 4.096
ep = namedtuple('ep', 'addr bits type')
adc_reset = ep(0x01, [8,9,10,11], 'wi')
adc_pll_reset =  ep(0x01, 17, 'wi')
adc_fifo_reset = ep(0x01, [18,19,20,21], 'wi')
adc_en0 =   ep(0x01, [12,13,14,15], 'wi')
v_scaling = 152.6e-6

data_set = [[],[],[],[]]

#data_set = []

start_time= time.time()
now = datetime.datetime.now()
current_time = now.strftime("%H_%M_%S")

#Should be half of the fifo size
transfer_length=(4096)

#One and only initialization of the hardware
f = FPGA()
if (False == f.init_device()):
    raise SystemExit
dev = ok.okCFrontPanel()
dev.OpenBySerial("")

def get_meta_data():
    meta_dict = {
        "Time" : (str)(current_time),
        "Date" : "{:%d, %b %Y}".format(datetime.date.today()),
        "Firmware version": f.xem.GetDeviceMajorVersion(),
        "Product" : f.xem.GetBoardModel(),
        "Product Serial Number" : f.xem.GetSerialNumber(),
        "Device ID" : f.xem.GetDeviceID(),
        "OS" : platform.system(),
        "OS Version" : platform.version()
    }
    return meta_dict

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
    
    '''
    convert readings from the AD796x to decimal values 
    unsigned 8bit integer buffer converted 
    (first revision populated the AD7961 (16 bits))
    '''

    bits = 16 # for AD7961 
    # bits=18 for AD7960
    d = np.frombuffer(buf, dtype=np.uint8).astype(np.uint32)
    if bits == 16:
        d2 = d[0::4] + (d[1::4] << 8)
    elif bits == 18:
        # TODO: test and verify  
        d2 = (d[3::4]<<8) + d[1::4] + ((d[0::4]<<16) & 0x03)
        # d2 = (d[3::4]<<8) + d[1::4] + ((d[0::4]<<16) & 0x03)

    d_twos = twos_comp(d2, bits)
    return d_twos

def adc_plot(fpga, adc_chan = 0, filename = None, PLT = False):
    s,e = fpga.read_pipe_out(addr_offset = adc_chan + 1, data_len=transfer_length)
    d = convert_data(s)
    v_scaling = 152.6e-6
    r=(d*v_scaling)
    return r,s,e

def set_bit(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])    
    f.xem.SetWireInValue(ep_bit.addr, mask, mask) # set
    f.xem.UpdateWireIns()

def clear_bit(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])    
    f.xem.SetWireInValue(ep_bit.addr, 0x0000, mask) # clear
    f.xem.UpdateWireIns()

def gen_mask(bit_pos):

    if not hasattr(bit_pos, '__iter__'):
        bit_pos = [bit_pos]

    mask = sum([(1 << b) for b in bit_pos])
    return mask 

#Creates a file with a single dataset, named with time of day
def filemaker(d1):
    nom = ("OPAMPDATA" + (str)(current_time)+ ".hdf5")
    hf = h5py.File(nom, 'w')

    for x in adc_list:
        hf.create_dataset((str)((str)(x)+ "dataset"), data=data_set[x.number])

    hf.close()
    data=get_meta_data()
    with open ('metadata' + (str) (current_time) + ".json", 'w') as outfile:
        json.dump(data, outfile)
    hdf5_reader(nom)


def hdf5_reader(nom):
    hf = h5py.File(nom, 'r')
    for x in hf.keys():
        n1= hf.get(x)
        n1 = np.array(n1)
        print ("This is one dataset and it's dimensions are: " + (str)(n1.shape))
        print (n1)

def toggle_high(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])
    f.xem.SetWireInValue(ep_bit.addr, mask, mask) # toggle high 
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(ep_bit.addr, 0x0000, mask)   # back low 
    f.xem.UpdateWireIns()

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
        
        if (adc_list[0].used):
            app= QtWidgets.QApplication(sys.argv)
            w =  MainWindow(chan=adc_list[0].number)
            w.show()
        if (adc_list[1].used):
            app2 = QtWidgets.QApplication(sys.argv)
            w2 = MainWindow(chan=adc_list[1].number)
            w2.show()
        if (adc_list[2].used):
            app3 = QtWidgets.QApplication(sys.argv)
            w3 = MainWindow(chan=adc_list[2].number)
            w3.show()
        if (adc_list[3].used):
            app4 = QtWidgets.QApplication(sys.argv)
            w4 = MainWindow(chan=adc_list[3].number)
            w4.show()
        
        sys.exit(app.exec_())

#Linked to the "exit" button on the main window 
def ex():
    sys.exit()

#This could be made easier, in a loop with objects
def selection_change(drop_down):
    return drop_down.currentText()

#Qt5 window class, to be initializaed upon call to Main.py
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self,chan, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.chan=chan
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.x = list(range(100))  # 100 time points
        self.y = [0 for _ in range(100)]  # 100 data points
        self.graphWidget.setBackground('w')
        self.setWindowTitle("Channel " + (str)(self.chan))
        self.setGeometry((500*self.chan), 50, 500, 300)
        pen = pg.mkPen(color=(255, 0, 0))
        self.cbs = [cb, cb2, cb3, cb4]
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        #closing the graph window(with the drop down menu)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()


    #Call to trig_check()  for interval, default is set to 0 ns
    def update_plot_data(self):
        '''if (Istriggered(adc_list[self.chan].trigaddr)):
        '''
        d,s,e =adc_plot(f, adc_chan=adc_list[self.chan].addr, PLT=False)
        data_set[self.chan].append(d)
        self.x = self.x[1:]  # Remove the first y element.
        a=(self.x[-1]+1)
        self.x.append(a)
        self.y = self.y[1:]  # Remove the first
        self.y = np.append(self.y, np.mean(d))

        for x in self.cbs:
            if selection_change(x)==("Channel " + (str)(self.chan +1) + " graphed"):
                self.data_line.setData(self.x, self.y)

        for y in self.cbs:
            if (selection_change(y)=="Channel " + (str)(self.chan+1) + " NOT graphed"):
                self.hide()

if __name__ == "__main__":
    print ('---FPGA ADC and DAC Controller---')
    f.one_shot(1)
        # reset PLL 
    toggle_high(adc_pll_reset)
    adc_chan = 0
    time.sleep(0.02)
    clear_bit(adc_reset, adc_chan = adc_chan)
    # reset FIFO
    toggle_high(adc_fifo_reset, adc_chan = adc_chan)
    # enable ADC
    set_bit(adc_reset, adc_chan = adc_chan)
    set_bit(adc_en0, adc_chan = adc_chan)

#This is to be changed, max voltage value allowed by the read
#This block creates the custom selection window
app = QApplication(sys.argv)
window = QWidget()
app.setStyle('Fusion')
window.setWindowTitle('covg_fpga')
app.setWindowIcon(QtGui.QIcon("qt5logo.png"))
layout = QVBoxLayout()
btn = QPushButton('Start Graphing')
btn.clicked.connect(main_loop)
bt = QPushButton('Exit')
bt.clicked.connect(ex)  
b = QPushButton('Save and Exit')
b.clicked.connect(save_and_exit)
cb = QComboBox()
cb.addItems(["Channel 1 graphed", "Channel 1 NOT graphed"])
cb2 = QComboBox()
cb2.addItems(["Channel 2 graphed", "Channel 2 NOT graphed"])
cb3 = QComboBox()
cb3.addItems(["Channel 3 graphed", "Channel 3 NOT graphed"])
cb4 = QComboBox()
cb4.addItems(["Channel 4 graphed", "Channel 4 NOT graphed"])
layout.addWidget(btn)
layout.addWidget(bt)
layout.addWidget(b)
layout.addWidget(cb)
layout.addWidget(cb2)
layout.addWidget(cb3)
layout.addWidget(cb4)
msg = QLabel('')
layout.addWidget(msg)
window.setLayout(layout)
window.setStyleSheet("background-color: grey")
window.setGeometry(500,200,500,200)
window.show()
