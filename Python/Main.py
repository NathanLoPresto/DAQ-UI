# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 13:17:08 2021

@author: Nathan LoPresto
"""
#External imports
import sys
from fpga import FPGA
import numpy as np
import matplotlib.pyplot as plt
import time
import pickle as pkl 
from drivers.utils import rev_lookup, bin, test_bit, twos_comp, gen_mask
from matplotlib import pyplot as plt
import matplotlib.animation as animation


#local imports 
from AD7960driver import y, adc_stream_mult, f
from graphadc import x, animate, terval, xs, ys, fig, trig

#Initializing the start time of the program
start_time= time.time()  

#Main loop     
if __name__ == "__main__":
    print ('---FPGA ADC and DAC Controller---')
    f = FPGA()
    if (False == f.init_device()):
        raise SystemExit
    f.one_shot(1)


    
    

    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=terval)
    plt.show()
