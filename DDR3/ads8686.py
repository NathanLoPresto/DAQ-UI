import sys
import os
from collections import namedtuple

cwd = os.getcwd() # gets the current working directory
path = os.path.join(cwd, "covg_fpga/python/drivers")
sys.path.append(path)

from fpga import FPGA
#from utils import rev_lookup, bin, test_bit, twos_comp

# Import the necessary functions from the script so we can initialize the device

################## Opal Kelly End Points ##################
ep = namedtuple('ep', 'addr bits type') # address of the DEVICE_ID reg so we can read it

# wire ins
control = ep(0x05, [i for i in range(32)], 'wi')  # note this is active low 

# wires out
mux_control = ep(0x01, 0, 'wi') # tells mux to choose the ADS8686 board
one_deep_fifo = ep(0x24, [i for i in range(32)], 'wo') # hands back the reset value of DEVICE_ID... should be 0x2002. Set to 1 for debugging

# triggers in 
valid      = ep(0x40, 11, 'ti')
fpga_reset = ep(0x40, 1, 'ti') 
fifo_reset = ep(0x40, 2, 'ti')

# triggers out
hall_full = ep(0x60, 1, 'to')

# pipeout (bits are meaningless)
adc_pipe = ep(0xA0, [i for i in range(32)], 'po') 

################## Define functions for fpga reading/sending data  ##################
def send_trig(ep_bit):
    ''' send a trigger to the opal kelly FPGA '''
    # expects a single bit in to control posedge (the ep_bit acts as that bit/var)
    f.xem.ActivateTriggerIn(ep_bit.addr, ep_bit.bits)

def read_wire(ep_bit): # reads the wire and returns the value back
    ''' read a wire in from the opal kelly FPGA 
        returns the value read
    '''
    f.xem.UpdateWireOuts()
    a = f.xem.GetWireOutValue(ep_bit.addr) 
    return a # returns the wire value into the v
################## Actual executing code ##################
# sets up the fpga by grabbing an instance of the class (as f) and initializing the device
f = FPGA(bitfile= 'logicwork.bit')
f.init_device() # programs the FPGA (loads bit file)

# set the SPI output mux to select a device other than the ADS7952 to avoid contention on SDO
#f.set_wire(mux_control.addr, 1, mask = mux_control.bits)