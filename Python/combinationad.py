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

#local imports
adc_chan=0
voltage_value = 4.096
ep = namedtuple('ep', 'addr bits type')
adc_pipe_rd_trig = ep(0x70, [3,4,5,6], 'to')
adc_pipe = ep(0xA1, [i for i in range(32)], 'po')
adc_reset = ep(0x01, [8,9,10,11], 'wi')
adc_pll_reset =  ep(0x01, 17, 'wi')
adc_fifo_reset = ep(0x01, [18,19,20,21], 'wi')
adc_en0 =   ep(0x01, [12,13,14,15], 'wi')
v_scaling = 152.6e-6

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
    s,e = fpga.read_pipe_out(addr_offset = adc_chan + 1)
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

def toggle_high(ep_bit, adc_chan = None):
    if adc_chan is None:
        mask = gen_mask(ep_bit.bits)
    else:
        mask = gen_mask(ep_bit.bits[adc_chan])
    f.xem.SetWireInValue(ep_bit.addr, mask, mask) # toggle high 
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(ep_bit.addr, 0x0000, mask)   # back low 
    f.xem.UpdateWireIns()

#Qt5 window class, to be initializaed upon call to Main.py
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))  # 100 time points
        self.y = [0 for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    #Call to trig_check()  for interval, default is set to 0 ns
    def update_plot_data(self):
        self.x = self.x[1:]  # Remove the first y element.
        a=(self.x[-1]+1)
        self.x.append(a)  # Add a new value 1 higher than the last.
        self.y = self.y[1:]  # Remove the first
        d,s,e =adc_plot(f, adc_chan=0, PLT=False)
        self.y.append(voltage_value*np.mean(d))  # Add a new random value.
        #appending to the evential HDF5 file
        self.data_line.setData(self.x, self.y)  # Update the data.

if __name__ == "__main__":
    print ('---FPGA ADC and DAC Controller---')
    f = FPGA()
    if (False == f.init_device()):
        raise SystemExit
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

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

#This is to be changed, max voltage value allowed by the read
