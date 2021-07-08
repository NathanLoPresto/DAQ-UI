import ok
from fpga import FPGA
import numpy as np
import random
import time
import array as arr
import matplotlib.pyplot as plot


CAPABILITY_CALIBRATION = 0x01
STATUS_CALIBRATION = 0x01
BLOCK_SIZE = 512
WRITE_SIZE=(8*1024*1024)
READ_SIZE = (8*1024*1024)
g_nMemSize = (8*1024*1024)

#amplitude of the signal in volts
amplitude_shift=5

#Higher number for slower frequency
frequency_shift =.25


NUM_TESTS = 10
READBUF_SIZE = (8*1024*1024)
g_buf = bytearray(np.asarray(np.ones(g_nMemSize), np.uint8))
tim = np.arange(0, 8388608, 1)
amplitude = (amplitude_shift*np.sin(tim/frequency_shift))
print ("the length of g_buf is: " , len(g_buf), "and the length of amp is: " , len(amplitude))
g_buf = bytearray(amplitude)
g_rbuf = bytearray(np.asarray(np.zeros(READBUF_SIZE), np.uint8))

def writeSDRAM():
    print ("Generating random data")

    #Reset FIFOs
    f.xem.SetWireInValue(0x00, 0x0004)
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(0x00, 0x0000)
    f.xem.UpdateWireIns()

    #Enable SDRAM write memory transfers
    f.xem.SetWireInValue(0x00, 0x0002)
    f.xem.UpdateWireIns()

    print ("Writing to DDR..")

    for i in range ((int)(g_nMemSize/WRITE_SIZE)):
        r = f.xem.WriteToBlockPipeIn( epAddr= 0x80, blockSize= BLOCK_SIZE,
                                      data= g_buf[(WRITE_SIZE*i):((WRITE_SIZE*i)+WRITE_SIZE)])
        print("Data size written is: ", r)
    print ("Done writing")
    print (g_buf[0:124])
    f.xem.UpdateWireOuts()

def readSDRAM():
    #Reset FIFOs
    f.xem.SetWireInValue(0x00, 0x0004)
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(0x00, 0x0000)
    f.xem.UpdateWireIns()
    #Enable SDRAM write memory transfers
    f.xem.SetWireInValue(0x00, 0x0001)
    f.xem.UpdateWireIns()
    print ("Reading from DDR")
    for i in range ((int)(g_nMemSize/WRITE_SIZE)):
        r = f.xem.ReadFromBlockPipeOut( epAddr= 0xA0, blockSize= BLOCK_SIZE,
                                      data= g_rbuf)
        print ("Length of read data is: ", r)
        
    if (g_rbuf==g_buf):
        print ("the DDR3 read/write worked")
    else:
        print("something went wrong")
    print (g_rbuf[0:124])
        
    
f = FPGA()
if (False == f.init_device()):
    raise SystemExit

#Wait for the configuration
time.sleep(10)
f.xem.UpdateWireOuts()
if (f.xem.GetWireOutValue(0x3e)!=0x01):
    print ("Capability calibration failure, will not continue script")
    quit()
if (f.xem.GetWireOutValue(0x20)!=0x01):
    print ("Status calibration errror, will not continue script")
    quit()
writeSDRAM()
readSDRAM()
