# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 18:28:04 2021

@author: nalo1
"""

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []

def trig_emulator(trig_addr, trig_mask):
  r = random.randint(0,10000)
  if (r==1):
    return True
  else:
    return False

def pipe_emulator():
  x=0
  for i in range (0,10):
    x = x + random.randint(0,10)
  return x



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

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('ADC output over time')
    plt.ylabel('ADC output')

# Set up plot to call animate() function periodically
while (True):
  if (trig_emulator(10101,10110)):
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), repeat=False)
    plt.show()