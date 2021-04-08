# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 19:11:58 2021

@author: Nathan LoPresto/Lucas Koerner
"""

from fpga import FPGA
import numpy as np
import matplotlib.pyplot as plt
from drivers.utils import bin,twos_comp

plt.ion()

#TODO: DO I need any of this, any of the functions that I pulled out
'''
from collections import namedtuple

ep = namedtuple('ep', 'addr bits type')
adc_reset = ep(0x01, [8,9,10,11], 'wi')  # note this is active low 
adc_en0 =   ep(0x01, [12,13,14,15], 'wi')
adc_en2 =   ep(0x01, 16, 'wi')
adc_pll_reset =  ep(0x01, 17, 'wi')
adc_fifo_reset = ep(0x01, [18,19,20,21], 'wi')

# wire outs for status 
adc_pll_lock =   ep(0x20, 8, 'wo')
adc_fifo_full =  ep(0x20, 9, 'wo')
adc_fifo_empty = ep(0x20, 10, 'wo')
pipe_out_rd_cnt = ep(0x20, [i+11 for i in range(10)], 'wo') # 10 bits 
ls_en = ep(0x20, 21, 'wo') # 10 bits 

# triggers out 
adc_pipe_rd_trig = ep(0x70, [3,4,5,6], 'to')

# pipeout (bits are meaningless)
# may change to array of addresses for each channel? 
adc_pipe = ep(0xA1, [i for i in range(32)], 'po') 

adc_chan = 0
'''
f=FPGA()


#needed for adc_stream_mult()
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

#returns the data needed for y()
def adc_stream_mult(adc, swps = 4):
    
    cnt = 0
    st = bytearray(np.asarray(np.ones(0, np.uint8)))  
    f.xem.UpdateTriggerOuts()
    
    while cnt<swps:
        if (f.xem.IsTriggered(0x60, 0x01)):
            s,e = adc.read_pipe_out()
            st += s 
            cnt = cnt + 1
            print(cnt)
        f.xem.UpdateTriggerOuts()

    d = convert_data(st)
    plt.plot(d)
    plt.show()
    return d

#function imported into graphadc for graphing
def y():
    a = adc_stream_mult(f,swps=4)
    return (int)(bin(a))

