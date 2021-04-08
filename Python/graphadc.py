# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 19:11:58 2021

@author: Nathan LoPresto
"""

#Imports for time and matplotlib
import time
from fpga import FPGA
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from register_map import ad5453
from AD7960driver import y

#Initializing the start time of the program
start_time= time.time()
# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []
f=FPGA()

def trig(trig_addr, trig_mask):
  
    f.xem.UpdateTriggerOuts()
    if (f.xem.IsTriggered(trig_addr, trig_mask)):
        return True
    else:
        return False
        
#Functions assigning values from pipeout to y, and time elapsed to x

def x():
    return float((int((time.time()-start_time)*10))/10)

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):
    
    if trig(ad5453['tx_register'], ad5453['control_register']):
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
    plt.title('The effect of time on value')
    plt.ylabel('Value')
    plt.xlabel('Time (seconds since start)')


ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), repeat=False)
plt.show()



