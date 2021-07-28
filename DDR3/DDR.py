import ok
from fpga import FPGA
import numpy as np
import time
import matplotlib.pyplot as plot
import struct
from collections import namedtuple

BLOCK_SIZE = (16384)
WRITE_SIZE=(8*1024*1024)
READ_SIZE = (8*1024*1024)
g_nMemSize = (8*1024*1024)
sample_size = (524288)
ep = namedtuple('ep', 'addr bits type')
control =   ep(0x00, [i for i in range(32)], 'wi')  # note this is active low 

# wire outs for "1 deep FIFO" 
one_deep_fifo =   ep(0x20, [i for i in range(32)], 'wo')

# triggers in 
valid      = ep(0x40, 0, 'ti')
fpga_reset = ep(0x40, 1, 'ti')
fifo_reset = ep(0x40, 2, 'ti')

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
    amplitude = amplitude.astype(np.int32)
    return time_axis, amplitude

#given a buffer, it writes a bytearray to the DDR3
def writeSDRAM(g_buf):

    print ("Length of buffer at the top of WriteSDRAM", len(g_buf))
    #Reset FIFOs
    f.set_wire(0x30, 4)
    f.set_wire(0x03, 0)
    f.set_wire(0x03, 2)

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
    f.set_wire(0x03, 4)
    f.set_wire(0x03, 0)
    f.set_wire(0x03, 1)

#reads to an empty array passed to the function
def readSDRAM():
    amplitude = np.zeros((sample_size,), dtype=int)
    pass_buf = bytearray(amplitude)
    #Reset FIFOs
    #below sets the HDL into read mode
    f.set_wire(0x03, 4)
    f.set_wire(0x03, 0)
    f.set_wire(0x03, 1)

    print ("Reading from DDR...")
    #Address changed to A5
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
def send_trig(ep_bit):
    ''' 
        expects a single bit, not yet implement for list of bits 
    '''
    f.xem.ActivateTriggerIn(ep_bit.addr, ep_bit.bits)

if __name__ == "__main__":

    f = FPGA(bitfile = '728.bit')
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
    write_sin_wave(2)
    f.xem.WriteRegister(0x80000010, 0x00003410)
    f.xem.ActivateTriggerIn(0x40, 8)
    #f.xem.UpdateWireOuts()
    #print (f.xem.GetWireOutValue(0x3E))

    '''
    time.sleep(2)
    dacs = [1,2,3,4]
    # SPI Master configuration: divide reg, ctrl reg, SS register 
    # MSB: 8 - set address, 4 - write data  

    # creg_val = 0x40003610 # Char length of 16; set both Tx_NEG, Rx_NEG; set ASS, IE. ADS7952
    creg_val = 0x40003010 # Char length of 16; clear both Tx_NEG, Rx_NEG; set ASS, IE. AD5453    
    # val = 0x40001fff # AD5453 (half-scale)

    for val in [0x80000051, 0x40000013,  # divider (need to look into settings of 1 and 2 didn't show 16 clock cycles) 
                0x80000041, creg_val,  # control register (CHAR_LEN = 16, bits 10,9, 13 and 12)
                0x80000061, 0x40000001]: # slave select (just setting bit0)

        f.set_wire(0x00, val, mask = 0xffffffff)
        send_trig(valid) 

    # now send SPI command 
    value = 0x40003FFF # AD5453 (half-scale)

    for val in [0x80000001, value,  # Tx register, data to send  
                0x80000041, creg_val | (1 << 8)]: # Control register - GO (bit 8)
        f.set_wire(0x00, val, mask = 0xffffffff)
        send_trig(valid) 
'''