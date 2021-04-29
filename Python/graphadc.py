# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 19:11:58 2021

@author: Nathan LoPresto
"""

#Imports for time, fpga, and matplotlib
import time
from matplotlib import pyplot as plt


#Receives the y values from AD7960
from AD7960driver import y

#Initializing the start time of the program
start_time= time.time()

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []


#Function assigning the difference between start time and time elapsed
def x():
    return float((int((time.time()-start_time)*10))/10)

#Animation function used in main, must draw from the register map
# This function is called periodically from FuncAnimation
def animate(i, xs, ys):
    

    xs.append(x())
    ys.append(y())
    
    # Limits the x and y lists to 50 variables 
    xs = xs[-50:]
    ys = ys[-50:]
    
    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('The effect of time on Voltage')
    plt.ylabel('Voltage')
    plt.xlabel('Time (seconds since start)')
