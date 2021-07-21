import ok
from fpga import FPGA
import numpy as np
import time
import matplotlib.pyplot as plot
import struct

BLOCK_SIZE = (16384)
WRITE_SIZE=(8*1024*1024)
READ_SIZE = (8*1024*1024)
g_nMemSize = (8*1024*1024)
sample_size = (524288)

#given the amplitude, and the time between each step, returns array to be plotted
def make_flat_voltage(input_voltage):
    time_axis = np.arange (0, np.pi*2 , (1/sample_size*2*np.pi) )
    amplitude = np.arange (0, np.pi*2 , (1/sample_size*2*np.pi) )
    for x in range (len(amplitude)):
        amplitude[x] = input_voltage
    amplitude = amplitude.astype(np.int32)
    return time_axis, amplitude

#Given the amplitude and period, returns an array to be plotted 
def make_sin_wave(amplitude_shift, frequency_shift=16):
    time_axis = np.arange (0, np.pi*2 , (1/sample_size*2*np.pi) )
    print ("length of time axis after creation ", len(time_axis))
    amplitude = (amplitude_shift*1000*np.sin(time_axis))
    y = len(amplitude)
    for x in range (y):
        amplitude[x]= amplitude[x]+(10000)
    for x in range (y):
        amplitude[x]= (int)(amplitude[x]/20000*16384)
    for x in range(y):
        amplitude[x] = amplitude[x]+5000
    amplitude = amplitude.astype(np.int32)
    return time_axis, amplitude

#given a buffer, it writes a bytearray to the DDR3
def writeSDRAM(g_buf):

    print ("Length of buffer at the top of WriteSDRAM", len(g_buf))
    #Reset FIFOs
    f.xem.SetWireInValue(0x03, 0x0004)
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(0x03, 0x0000)
    f.xem.UpdateWireIns()

    #Enable SDRAM write memory transfers
    f.xem.SetWireInValue(0x03, 0x0002)
    f.xem.UpdateWireIns()
    print ("Writing to DDR...")
    time1 = time.time()
    #for i in range ((int)(len(g_buf)/WRITE_SIZE)):
    r = f.xem.WriteToBlockPipeIn( epAddr= 0x80, blockSize= BLOCK_SIZE,
                                      data= g_buf[0:(len(g_buf))])
    print ("The length of the write is ", r)
    
    time2 = time.time()
    time3  = (time2-time1)
    mbs = (int)(r/1024/1024/ time3)
    print ("The speed of the write was ", mbs, " MegaBytes per second")

    #below sets the HDL into read mode
    f.xem.UpdateWireOuts()
    f.xem.SetWireInValue(0x03, 0x0004)
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(0x03, 0x0000)
    f.xem.UpdateWireIns()
    #Enable SDRAM write memory transfers
    f.xem.SetWireInValue(0x03, 0x0001)
    f.xem.UpdateWireIns()

#reads to an empty array passed to the function
def readSDRAM():
    amplitude = np.zeros((sample_size,), dtype=int)
    pass_buf = bytearray(amplitude)
    #Reset FIFOs
    #below sets the HDL into read mode
    f.xem.UpdateWireOuts()
    f.xem.SetWireInValue(0x03, 0x0004)
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(0x03, 0x0000)
    f.xem.UpdateWireIns()
    #Enable SDRAM write memory transfers
    f.xem.SetWireInValue(0x03, 0x0001)
    f.xem.UpdateWireIns()
    print ("Reading from DDR...")
    for i in range ((int)(g_nMemSize/WRITE_SIZE)):
        r = f.xem.ReadFromBlockPipeOut( epAddr= 0xA0, blockSize= BLOCK_SIZE,
                                      data= pass_buf)
        print ("The length of the read is:", r)
    return pass_buf

#given a buffer, it unpacks into into human readable float values
def unpack(buf):
    unpacked_var = []
    for x in range (sample_size):
        unpacked_var.append(struct.unpack('i', buf[(x*4):((x+1)*4)]))
    return unpacked_var

#Given two arrays, plots the x and y axis with hardcoded axis names 
def testplot(x_axis, y_axis):
    plot.plot(x_axis, y_axis)
    plot.title('The outputted wave should look like this')
    plot.xlabel('time')
    plot.ylabel('amplitude (millivolts)')
    plot.grid(True, which = 'both')
    plot.axhline(y=0, color = 'k')
    plot.show()

#given an amplitude and a period, it will write a waveform to the DDR3
def write_sin_wave (a):
    time_axis, g_buf_init = make_sin_wave(a)
    print ("The length of the array before casting ", len(g_buf_init))
    pass_buf = bytearray(g_buf_init)
    writeSDRAM(pass_buf)

#given and amplitude and a period, it will write a step function to the DDR3 
def write_flat_voltage(input_voltage):
    time_axis, g_buf_init = make_flat_voltage(input_voltage)
    pass_buf2 = bytearray(g_buf_init)
    writeSDRAM(pass_buf2)

#Reads and prints the contents of the DDR3
def print_DDR3():
    g_rbuf = readSDRAM()
    unpacked_g_rbuf = np.array(unpack(g_rbuf)).astype('float64')
    for x in range (len(unpacked_g_rbuf)):
        unpacked_g_rbuf[x] = (unpacked_g_rbuf[x]/1000)
    testplot(np.arange (0, sample_size, 1), unpacked_g_rbuf)

if __name__ == "__main__":

    f = FPGA(bitfile = 'OldVersion2.bit')
    if (False == f.init_device()):
        raise SystemExit
    #Wait for the configuration
    time.sleep(3)
    factor = (int)(sample_size/8)
    f.xem.SetWireInValue(0x04, factor)
    #f.xem.SetWireInValue(0x04, 0xFF)
    f.xem.UpdateWireIns()

    #Sample rate speed, to bits 18:9
    f.xem.SetWireInValue(0x02, 0x0000A000, 0x0003FF00 )
    f.xem.UpdateWireIns()
    write_flat_voltage(10000)
    time.sleep(2)
    f.xem.UpdateWireOuts()
    print (f.xem.GetWireOutValue(0x3E))