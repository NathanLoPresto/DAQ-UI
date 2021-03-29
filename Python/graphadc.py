#Imports for time and matplotlib
import random
import time
from matplotlib import pyplot as plt
import matplotlib.animation as animation

#Initializing the start time of the program
start_time= time.time()
#Time between each trigger check and append
terval=200
# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []

def trig():
    #trigger address and mask
    trig_addr = 0x60
    trig_mask = 0x01

    fpga.xem.UpdateTriggerOuts()
    if (fpga.xem.IsTriggered(trig_addr, trig_mask)):
        return True
    else:
        return False
        
#Functions assigning values from pipeout to y, and time elapsed to x
def y():
   return random.randint(0,10)

def x():
    return float((int((time.time()-start_time)*10))/10)

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):
    
    if trig():
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


ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=terval)
plt.show()


