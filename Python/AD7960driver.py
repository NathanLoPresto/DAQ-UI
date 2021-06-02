# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 19:11:58 2021

@author: Nathan LoPresto/Lucas Koerner
"""
import numpy as np
import numpy
import random

#will need fpga imports in the final iteration
from fifousb import fifo_read, trig_addr


voltage_value = 4.09


def trig_emulator():
  return trig_addr()

def twos_comp(val, bits):
    """compute the 2's complement of int value val
        handle an array (list or numpy)
    """

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
    bits = 18 # for AD7961 bits=18 for AD7960
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
