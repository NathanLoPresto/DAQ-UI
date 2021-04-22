# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 18:28:04 2021

@author: Nathan loPresto
"""
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []

def trig_emulator():
  r = random.randint(0,10000)
  if (r==1):
    return True
  else:
    return False

def pipe_emulator():
  #creates a size 10 array with random numbers 0-4096
  x=np.array([np.round(4096*np.random.rand(1,10))])
  #prints the arrays in the terminal window with time stamps
  print(dt.datetime.now().strftime('%H:%M:%S.%f'))
  print (x)
  newdata = np.squeeze(x)
  return newdata

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):

    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(pipe_emulator())

    # Limit x and y lists to 20 items
    xs = xs[-20:]
    ys = ys[-20:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)
 
    #dark mode setup
    ax.set_facecolor('black')
    ax.set_facecolor((0.5, 0.5, 0.5))

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('ADC output over time')
    plt.ylabel('ADC output')

# Set up plot to call animate() function periodically
while (True):
  if (trig_emulator()):
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), repeat=False)
    plt.show()
