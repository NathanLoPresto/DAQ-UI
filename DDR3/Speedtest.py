import ok
from fpga import FPGA
import numpy as np
import time
import matplotlib.pyplot as plot
import struct
import csv

BLOCK_SIZE = (16384)
WRITE_SIZE=(8*1024*1024)
READ_SIZE = (8*1024*1024)
g_nMemSize = (8*1024*1024)
sample_size = (524288)


#Given the amplitude and period, returns an array to be plotted 
def make_sin_wave(amplitude_shift, frequency_shift=16):
    time_axis = np.arange (0, np.pi*2 , (1/sample_size*2*np.pi) )
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

    #Reset FIFOs
    f.xem.SetWireInValue(0x03, 0x0004)
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(0x03, 0x0000)
    f.xem.UpdateWireIns()

    #Enable SDRAM write memory transfers
    f.xem.SetWireInValue(0x03, 0x0002)
    f.xem.UpdateWireIns()
    time1 = time.time()
    #for i in range ((int)(len(g_buf)/WRITE_SIZE)):
    r = f.xem.WriteToBlockPipeIn( epAddr= 0x80, blockSize= BLOCK_SIZE,
                                      data= g_buf[0:(len(g_buf))])
    
    time2 = time.time()
    time3  = (time2-time1)
    mbs = (int)(r/1024/1024/ time3)

    #below sets the HDL into read mode
    f.xem.UpdateWireOuts()
    f.xem.SetWireInValue(0x03, 0x0004)
    f.xem.UpdateWireIns()
    f.xem.SetWireInValue(0x03, 0x0000)
    f.xem.UpdateWireIns()
    #Enable SDRAM write memory transfers
    f.xem.SetWireInValue(0x03, 0x0001)
    f.xem.UpdateWireIns()
    return mbs

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
    time1 = time.time()

    for i in range ((int)(g_nMemSize/WRITE_SIZE)):
        g = f.xem.ReadFromBlockPipeOut( epAddr= 0xA0, blockSize= BLOCK_SIZE,
                                      data= pass_buf)
        
    time2 = time.time()
    time3  = (time2-time1)
    mbs = (int)(g/1024/1024/ time3)
    return mbs

#given an amplitude and a period, it will write a waveform to the DDR3
def write_sin_wave (a):
    time_axis, g_buf_init = make_sin_wave(a)
    pass_buf = bytearray(g_buf_init)
    d = writeSDRAM(pass_buf)
    return d

if __name__ == "__main__":

    f = FPGA(bitfile = 'Withpipeout.bit')
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
    Header = ["Read/Write speeds in MB/s with block length 512",
    "Read/Write speeds in MB/s with block length 1024",
    "Read/Write speeds in MB/s with block length 2048",
    "Read/Write speeds in MB/s with block length 4096",
    "Read/Write speeds in MB/s with block length 8192",
    "Read/Write speeds in MB/s with block length 16384",]
    write_speed = []
    read_speed = []
    for x in range (6):
        BLOCK_SIZE = (512*(2**(x))) 
        for y in range (3):
            write_speed.append(write_sin_wave(3))
            read_speed.append(readSDRAM())

    with open('Speedtest.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)


        for x in range (6):
            # write the header
            writer.writerow(Header[x:(x+1)])
            writer.writerow(read_speed[(x*3):((x+1)*3)])
            writer.writerow(write_speed[(x*3):((x+1)*3)])

