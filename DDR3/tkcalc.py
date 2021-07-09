import numpy as np
import matplotlib.pyplot as plot
import struct
WRITE_SIZE = (64)

def make_sin_wave(amplitude_shift, frequency_shift):
    time_axis = np.arange (0, 50, 1)
    amplitude = (amplitude_shift*100*np.sin(time_axis*frequency_shift))
    for x in range (len(amplitude)):
        amplitude[x] = (int)(amplitude[x])
    amplitude = amplitude.astype(np.int32)
    return time_axis, amplitude

def test_plot(x_axis, y_axis):
    plot.plot(x_axis, y_axis)
    plot.title('Sinewave')
    plot.xlabel('time_axise')
    plot.ylabel('amplitude')
    plot.grid(True, which = 'both')
    plot.axhline(y=0, color = 'k')
    plot.show()

def unpack(buf):
    unpacked_var = []
    print (len(buf))
    for x in range (50):
        unpacked_var.append(struct.unpack('i', buf[(x*4):((x+1)*4)]))
    return unpacked_var

time_array , amp_array = make_sin_wave(1,1)
print (amp_array)
print (time_array)
print (type(amp_array[0]))
print (type(time_array[0]))
buf_time_array = bytearray(time_array)
buf_amp_array = bytearray (amp_array)
unpacked_time = unpack(buf_time_array)
unpacked_amp = unpack(buf_amp_array)
test_plot(unpacked_time, unpacked_amp)
