# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 13:17:08 2021

@author: Nathan LoPresto
"""
#External imports
from fpga import FPGA
import matplotlib.pyplot as plt
import time
from drivers.utils import rev_lookup, bin, test_bit, twos_comp, gen_mask
from matplotlib import pyplot as plt
import matplotlib.animation as animation


#local imports 
from graphadc import animate,xs, ys, fig, trig
from register_map import ad5453, ad7952

#Initializing the start time of the program
start_time= time.time()  

#Main loop     
if __name__ == "__main__":
    print ('---FPGA ADC and DAC Controller---')
    f = FPGA()
    if (False == f.init_device()):
        raise SystemExit
    f.one_shot(1)


    
    
    while (trig(ad5453['tx_register'], ad7952['control_register'])):
        ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), repeat=False)
        plt.show()

