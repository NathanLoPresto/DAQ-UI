# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 13:17:08 2021

@author: Nathan LoPresto
"""
#External imports
from threading import Thread
import time
#from drivers.utils import rev_lookup, bin, test_bit, twos_comp, gen_mask
import sys
from PyQt5 import QtWidgets

#local imports 
from fifousb import trig_addr
from pyqtgraphing import MainWindow
from fpga import FPGA

#Initializing the start time of the program
start_time= time.time()  

class myThread(Thread):
    def __init__(self, value):
        Thread.__init__(self)
        self.value = value

    def run(self):
      if (self.value==1):
        print ("going")
      else:
        sec_thread()

def sec_thread():
  x=0
  while (x<17):
    print ("Hello I am the second function")
    x= x+1  
#Runs indefinately, checking for trigger to start reading ADC data and plotting
#Can add exit parameters later.
#(possibly time or number of calls to func.animate)

#creates the threads that you want, sets their instance variables

Secondthread = myThread(2)

#Starts the threads

Secondthread.start()

while (True):
        if (trig_addr()):
            app = QtWidgets.QApplication(sys.argv)
            w = MainWindow()
            w.show()
            sys.exit(app.exec_())
