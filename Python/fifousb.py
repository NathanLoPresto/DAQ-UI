# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 11:55:57 2021

@author: Nathan LoPresto
"""

#in the end, I intend for this class to be drawn by ad7960driver
import ok
from fpga import FPGA
from collections import namedtuple

f = FPGA()

f.init_device()
dev = ok.okCFrontPanel()
 
dev.OpenBySerial("")
error = dev.ConfigureFPGA("example.bit")
# It’s a good idea to check for errors here!!

ep = namedtuple('ep', 'addr bits type')

adc_pipe = ep(0xA1, [i for i in range(32)], 'po') 
adc_pipe_rd_trig = ep(0x70, [3,4,5,6], 'to')

def fifo_read(): 
    # Send brief reset signal to initialize the FIFO
    buf,e  = f.read_pipe_out(0xA1)
    return buf
    dev.reset_device()

def trig_addr():
    dev.UpdateTriggerOuts()
    tf = dev.IsTriggered(0x70, 0x80)
    return tf
