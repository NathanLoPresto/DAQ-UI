from PyQt5 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget, plot
from collections import namedtuple
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from scipy import signal
import pyqtgraph as pg
from fpga import FPGA 
import numpy as np
import datetime
import platform
import os.path
import time
import json
import h5py
import sys
import ok

#Input your values for adc address, if used, and downsample factor
ep                = namedtuple('ep', 'number addr used downsample_factor')
ad5453            = ep(0, 0xA0, True,  1)
ad7960            = ep(1, 0xA1, True,  1)
ads7952           = ep(2, 0xA0, False, 1)
ads8686           = ep(3, 0xA0, False, 1)
adc_list          = [ad5453, ad7960, ads7952, ads8686]

#These will eventually be taken from top-down file
save_hdf5         = 'C:/Users/nalo1/Downloads/HDF5'
save_json         = 'C:/Users/nalo1/Downloads/Metadata'

#Data_Set should add more rows if more ADC inputs
start_time        = time.time()
now               = datetime.datetime.now()
current_time      = now.strftime("%H_%M_%S")
pipe_addr_list    = [0x80, 0x80]
data_set          = [[],[],[],[]]

SAMPLE_SIZE       = (524288)
BLOCK_SIZE        = (16384)
WRITE_SIZE        = (8*1024*1024)
TRANSFER_LENGTH   = (4096)
G_NMEMSIZE        = (8*1024*1024)
V_SCALING         = 152.6e-6

#Creates both an HDF5 file with data, and JSON with metadata
def filemaker():
    nom = os.path.join(save_hdf5,"OPAMPDATA" + (str)(current_time)+ ".hdf5")
    hf  = h5py.File(nom, 'w')
    for x in adc_list:
        hf.create_dataset((str)((str)(x)+ "dataset"), data=data_set[x.number])
    hf.close()

    data = get_meta_data()
    nom2 = os.path.join(save_json,'metadata' + (str) (current_time) + ".json")
    with open (nom2, 'w') as outfile:
        json.dump(data, outfile)

#Used as a twos_comp converter for the convert_data function
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

#Given a buffer from the read_pipe, converts into float-type for graphing
def convert_data(buf):
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

#Read from pipe-out, returns a float-array for graphing
def adc_return(fpga, adc_chan = 0, filename = None, PLT = False):
    s,e       = fpga.read_pipe_out(addr_offset = adc_chan, data_len=TRANSFER_LENGTH)
    d         = convert_data(s)
    r         = (d*V_SCALING)
    return r

#returns a dictionary of metadata for JSON file creation
def get_meta_data():
    meta_dict = {
        "Time"                  : (str)(current_time),
        "Date"                  : "{:%d, %b %Y}".format(datetime.date.today()),
        "Firmware version"      : f.xem.GetDeviceMajorVersion(),
        "Product"               : f.xem.GetBoardModel(),
        "Product Serial Number" : f.xem.GetSerialNumber(),
        "Device ID"             : f.xem.GetDeviceID(),
        "OS"                    : platform.system(),
        "OS Version"            : platform.version()
    }
    return meta_dict

#Called by Control-C During graphing to save data and exit the program
def save_and_exit():
  print ("Saving and exiting the program")
  if (len(data_set)!=0):
    filemaker()
  sys.exit()

#Given the amplitude and period, returns an array to be plotted 
def make_sin_wave(amplitude_shift):
    time_axis = np.arange (0, np.pi*2 , (1/SAMPLE_SIZE*2*np.pi) )
    amplitude = (amplitude_shift*1000*np.sin(time_axis))
    y = len(amplitude)
    for x in range (y):
        amplitude[x] = amplitude[x]+(10000)
    for x in range (y):
        amplitude[x] = (int)(amplitude[x]/20000*16384)
    for x in range(y):
        amplitude[x] = amplitude[x]+5000
    amplitude = amplitude.astype(np.int32)
    byteamp = bytearray(amplitude)
    return byteamp

#Given a single 14-bit value, writes full data set at that DAC value
def make_flat_voltage(input_voltage):
    time_axis = np.arange (0, np.pi*2 , (1/SAMPLE_SIZE*2*np.pi) )
    amplitude = np.arange (0, np.pi*2 , (1/SAMPLE_SIZE*2*np.pi) )
    for x in range (len(amplitude)):
        amplitude[x] = input_voltage
    amplitude = amplitude.astype(np.int32)
    byteamp = bytearray(amplitude)
    return byteamp

#Given a buffer and DDR address, writes to SDRAM
def writeSDRAM(g_buf, address):
    #Reset FIFOs
    f.set_wire(0x30, 4)
    f.set_wire(0x03, 0)
    f.set_wire(0x03, 2)

    r = f.xem.WriteToBlockPipeIn( epAddr= address, blockSize= BLOCK_SIZE,
                                      data= g_buf[0:(len(g_buf))])
    print ("Written length was: ", r)

    #below sets the HDL into read mode
    f.set_wire(0x03, 4)
    f.set_wire(0x03, 0)
    f.set_wire(0x03, 1)

#Creates 4 graphing windows if enabled, sends pinter to ADC namedtuple
def main_loop():
    if (f.xem.NoError != f.xem.OpenBySerial("")):
            print ("You can't run the software if no device is detected")
            return(False)
    else:
        app= QtWidgets.QApplication(sys.argv)
        obj_list= []
        for x in range(len(adc_list)):
            if (adc_list[x].used):
                obj = MainWindow(chan=adc_list[x].number)
                obj_list.append(obj)
                
        for y in obj_list:
            y.show()
            
        sys.exit(app.exec_())

#Qt5 window class, to be initializaed upon call to main loop
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
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        #closing the graph window(with the drop down menu)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    #Call to trig_check()  for interval, default is set to 0 ns
    def update_plot_data(self):
        try:
            d = adc_return(f, adc_chan=adc_list[self.chan].addr, PLT=False)
            d = signal.decimate(d, adc_list[self.chan].downsample_factor)
            data_set[self.chan].append(d)
            self.x = self.x[1:]  # Remove the first y element.
            a=(self.x[-1]+1)
            self.x.append(a)
            self.y = self.y[1:]  # Remove the first
            self.y = np.append(self.y, np.mean(d))
            self.data_line.setData(self.x, self.y)
        except KeyboardInterrupt:
            save_and_exit()

#Initialized FPGA and runs main loop
#TODO: Check PLL reset from UI.py
if __name__ == "__main__":

    f = FPGA(bitfile = 'pipe1.bit')
    if (False == f.init_device()):
        raise SystemExit
            # reset PLL 

    #This will eventually be moved to the input script
    input_list = []
    input_list.append(make_sin_wave(3))
    input_list.append(make_flat_voltage(10000))

    #writes all of the inputted sine waves into the DDR3
    for x in  range (len(input_list)):
        writeSDRAM(input_list[x], pipe_addr_list[x] )

    input("Press Enter to start")
    main_loop()
