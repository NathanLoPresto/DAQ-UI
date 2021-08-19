from fpga import FPGA
import numpy as np
import ok
import sys

bitfile_used = 'hostsspeed3.bit'

tests= 150

if __name__ == "__main__":
    f = FPGA(bitfile = bitfile_used)
    if (False == f.init_device()):
        print("Configuration failed")
        sys.exit()
    vals = []

    while (len(vals)<tests):
        f.xem.UpdateTriggerOuts()
        if (f.xem.IsTriggered(0x61, 0xFFFF)):
            f.xem.ActivateTriggerIn(0x41, 0x01)
            f.xem.UpdateWireOuts()
            val = f.xem.GetWireOutValue(0x20)
            vals.append(val)

    for x in range(len(vals)):
        vals[x]/=200000000
    
    print("Mean time through host is: " , 1000*np.mean(vals), " milliseconds")
    print("Amount of tests: ", tests)
