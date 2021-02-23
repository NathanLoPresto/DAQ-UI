#Imports for time and matplotlib
import time
from matplotlib import pyplot as plt
import matplotlib.animation as animation

#opening and enumerating the opalkelly device
dev = ok.okCFrontPanel()
dev.OpenBySerial("")
dev.ConfigureFPGA("example.bit")

#addresses and masks for pipes and triggers
pipeaddress= 0xa0
trigaddress = 0x71
trigmask = 0x80

#Time between each trigger check and append
terval=500

#Initializing the start time of the program
start_time= time.time()

#checking for trigger, returns boolean 
def trig():
    dev.UpdateTriggerOuts()
    if dev.IsTriggered(trigaddress, trigmask):
        return True
    else:
        return False
    
# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []

#creates a bytearray for pipeout
datain = bytearray('00000000000000000000000000')

#Functions assigning values from pipeout to y, and time elapsed to x
def y():
   return dev.ReadFromPipeOut(pipeaddress, datain)

def x():
    return float((int((time.time()-start_time)*10))/10)

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):
    #if triggered, append x and y values
    if trig():
        xs.append(x())
        ys.append(y())
    
    #printing x and y array values
        print("The x values are: ", xs)
        print("The y values are: ", ys)
    
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

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=terval)
plt.show()
