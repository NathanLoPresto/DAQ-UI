import ok
from fpga import FPGA
import numpy as np
import random
import time
import array as arr
import matplotlib.pyplot as plot
import struct

CAPABILITY_CALIBRATION = 0x01
STATUS_CALIBRATION = 0x01
BLOCK_SIZE = 512
WRITE_SIZE=(8*1024*1024)
READ_SIZE = (8*1024*1024)
g_nMemSize = (8*1024*1024)

NUM_TESTS = 10
READBUF_SIZE = (8*1024*1024)

def make_sin_wave(amplitude_shift, frequency_shift):
    time_axis = np.arange (0, 2097152, 1)
    amplitude = (amplitude_shift*100*np.sin(time_axis*frequency_shift))
    for x in range (len(amplitude)):
        amplitude[x] = (int)(amplitude[x])
    amplitude = amplitude.astype(np.int32)
    return time_axis, amplitude

def writeSDRAM():

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
        print("Data size written is: ", r)
    end_write = time.time()
    change_write = (end_write - start_write)
    write_speed = (g_nMemSize/change_write)
    print ("The speed of the write is ", write_speed, " bits per second")
    f.xem.UpdateWireOuts()

def readSDRAM():
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
        print ("Length of read data is: ", r)
    end_read = time.time()
    change_read = (end_read - start_read)
    read_speed = (g_nMemSize/change_read)
    print ("The speed of the read was: ", read_speed, " bits per second")

def unpack(buf):
    unpacked_var = []
    print (len(buf))
    for x in range (50):
        unpacked_var.append(struct.unpack('i', buf[(x*4):((x+1)*4)]))
    return unpacked_var

def testplot(x_axis, y_axis):
    plot.plot(x_axis, y_axis)
    plot.title('Sinewave')
    plot.xlabel('time')
    plot.ylabel('amplitude')
    plot.grid(True, which = 'both')
    plot.axhline(y=0, color = 'k')
    plot.show()

if __name__ == "__main__":
    f = FPGA()
    if (False == f.init_device()):
        raise SystemExit

    #Wait for the configuration
    time.sleep(10)
    f.xem.UpdateWireOuts()
    g_buf = bytearray(np.asarray(np.ones(g_nMemSize), np.uint8))
    time_axis, g_buf_init = make_sin_wave(1,100)
    g_buf = bytearray(g_buf_init)
    g_rbuf = bytearray(np.asarray(np.zeros(READBUF_SIZE), np.uint8))

    if (f.xem.GetWireOutValue(0x3e)!=0x01):
        print ("Capability calibration failure, will not continue script")
        quit()
    if (f.xem.GetWireOutValue(0x20)!=0x01):
        print ("Status calibration errror, will not continue script")
        quit()
    writeSDRAM()
    readSDRAM()
    unpacked_g_rbuf = unpack(g_rbuf)
    print (unpacked_g_rbuf)
