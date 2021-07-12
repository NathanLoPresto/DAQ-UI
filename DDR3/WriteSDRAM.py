import ok
from fpga import FPGA
import numpy as np
import time
import matplotlib.pyplot as plot
import struct

CAPABILITY_CALIBRATION = 0x01
STATUS_CALIBRATION = 0x01
BLOCK_SIZE = 512
WRITE_SIZE=(8*1024*1024)
READ_SIZE = (8*1024*1024)
g_nMemSize = (8*1024*1024)
AXIS_SIZE = (1024*1024*2)
#Amplitude of the waveform in volts
AMP_PARAM =10

#Period of the waveform in seconds
FREQUENCY_PARAM = 10

READBUF_SIZE = (8*1024*1024)

#given the amplitude, and the time between each step, returns array to be plotted
def make_step_function(amplitude_shift, frequency_step):
    time_axis = np.arange (0, AXIS_SIZE, 1)
    amplitude = np.arange(0,AXIS_SIZE, 1)
    for x in range (len(amplitude)):
        if (x%frequency_step<(frequency_step/2)):
            amplitude[x] = (amplitude_shift*100)
        else:
            amplitude[x] = 0
    amplitude = amplitude.astype(np.int32)
    return time_axis, amplitude

#Given the amplitude and period, returns an array to be plotted 
def make_sin_wave(amplitude_shift, frequency_shift):
    frequency_shift = frequency_shift/np.pi/2
    time_axis = np.arange (0, AXIS_SIZE, 1)
    amplitude = (amplitude_shift*100*np.sin(time_axis/frequency_shift))
    for x in range (len(amplitude)):
        amplitude[x] = (int)(amplitude[x])
    amplitude = amplitude.astype(np.int32)
    return time_axis, amplitude

#given a buffer, it writes a bytearray to the DDR3
def writeSDRAM(g_buf):

    start_write = time.time()
    #Reset FIFOs
    f.xem.SetWireInValue(0x00, 0x0004)
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(0x00, 0x0000)
    f.xem.UpdateWireIns()

    #Enable SDRAM write memory transfers
    f.xem.SetWireInValue(0x00, 0x0002)
    f.xem.UpdateWireIns()

    print ("Writing to DDR...")

    for i in range ((int)(g_nMemSize/WRITE_SIZE)):
        r = f.xem.WriteToBlockPipeIn( epAddr= 0x80, blockSize= BLOCK_SIZE,
                                      data= g_buf[(WRITE_SIZE*i):((WRITE_SIZE*i)+WRITE_SIZE)])
    end_write = time.time()
    change_write = (end_write - start_write)
    write_speed = (1/change_write)
    print ("The speed of the write was ", (int)(write_speed), " MegaBytes per second")
    f.xem.UpdateWireOuts()

#reads to an empty array passed to the function
def readSDRAM(g_rbuf):
    start_read = time.time()
    #Reset FIFOs
    f.xem.SetWireInValue(0x00, 0x0004)
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(0x00, 0x0000)
    f.xem.UpdateWireIns()
    #Enable SDRAM write memory transfers
    f.xem.SetWireInValue(0x00, 0x0001)
    f.xem.UpdateWireIns()
    print ("Reading from DDR...")
    for i in range ((int)(g_nMemSize/WRITE_SIZE)):
        r = f.xem.ReadFromBlockPipeOut( epAddr= 0xA0, blockSize= BLOCK_SIZE,
                                      data= g_rbuf)
    end_read = time.time()
    change_read = (end_read - start_read)
    read_speed = (1/change_read)
    print ("The speed of the read was ", (int)(read_speed), " MegaBytes per second")

#given a buffer, it unpacks into into human readable float values
def unpack(buf):
    unpacked_var = []
    for x in range (50):
        unpacked_var.append(struct.unpack('i', buf[(x*4):((x+1)*4)]))
    return unpacked_var

#Given two arrays, plots the x and y axis with hardcoded axis names 
def testplot(x_axis, y_axis):
    plot.plot(x_axis, y_axis)
    plot.title('Sinewave')
    plot.xlabel('time')
    plot.ylabel('amplitude')
    plot.grid(True, which = 'both')
    plot.axhline(y=0, color = 'k')
    plot.show()

#given an amplitude and a period, it will write a waveform to the DDR3
def write_sin_wave (a, b):
    g_buf = bytearray(np.asarray(np.ones(g_nMemSize), np.uint8))
    time_axis, g_buf_init = make_sin_wave(a,b)
    g_buf = bytearray(g_buf_init)
    writeSDRAM(g_buf)

#given and amplitude and a period, it will write a step function to the DDR3 
def write_step_func(a,b):
    g_buf = bytearray(np.asarray(np.ones(g_nMemSize), np.uint8))
    time_axis, g_buf_init = make_step_function(a,b)
    g_buf = bytearray(g_buf_init)
    writeSDRAM(g_buf)

#Reads and prints the contents of the DDR3
def print_DDR3():
    g_rbuf = bytearray(np.asarray(np.zeros(READBUF_SIZE), np.uint8))
    readSDRAM(g_rbuf)
    unpacked_g_rbuf = np.array(unpack(g_rbuf)).astype('float64')
    for x in range (len(unpacked_g_rbuf)):
        unpacked_g_rbuf[x] = (unpacked_g_rbuf[x]/100)
    print (unpacked_g_rbuf)
    testplot(np.arange (0, len(unpacked_g_rbuf), 1), unpacked_g_rbuf)

if __name__ == "__main__":
    f = FPGA()
    if (False == f.init_device()):
        raise SystemExit

    #Wait for the configuration
    time.sleep(3)

    f.xem.UpdateWireOuts()
    
    write_sin_wave(10,10)
    print_DDR3()
    write_step_func(10,10)
    print_DDR3()
