import numpy as np
import numpy
import random
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

voltage_value = 4.09

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
    bits = 16 # for AD7961 bits=18 for AD7960
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
  y = Arr_to_int(convert_data(Read_Pipe_Out()))
  print (y*voltage_value/131072)
  return (y*voltage_value/131072)

def Read_Pipe_Out():
  r = np.round(4096*np.random.rand(16))
  return r

def Arr_to_int(y):
  t=0
  for i in range (len(y)-1):
    t = t + y.item(i)
  return t

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):

    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(y())

    # Limit x and y lists to 20 items
    xs = xs[-20:]
    ys = ys[-20:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)
 
    #dark mode setup
    ax.set_facecolor('black')
    ax.set_facecolor((.5, .5, .5))

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Voltage output over time')
    plt.ylabel('Volts (V)')

# Set up plot to call animate() function periodically
while (True):
  if (trig_emulator()):
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), repeat=False)
    plt.show()
