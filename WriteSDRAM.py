import ok
from fpga import FPGA
import numpy as np
import random
f = FPGA()
if (False == f.init_device()):
    raise SystemExit
    
WRITE_SIZE=(8*1024*1024)
READ_SIZE = (8*1024*1024)
BLOCK_SIZE = 512#bytes
g_nMemSize=(2*512*1024*1024)
OK_INTERFACE_UNKNOWN = 0
OK_INTERFACE_USB2 = 1
OK_INTERFACE_PCIE = 2
OK_INTERFACE_USB3 = 3
READBUF_SIZE = (8*1024*1024)
print("Generating random data.....")
g_buf = bytearray(np.asarray(np.ones(BLOCK_SIZE), np.uint8))
print(g_buf)
g_nMems=0
infodev = ok.okTDeviceInfo()
f.xem.GetDeviceInfo(infodev)


def writeSDRAM():

    
    infoDev= ok.okTDeviceInfo()
    f.xem.GetDeviceInfo(infoDev)

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
        r = f.xem.WriteToPipeIn( epAddr= 0x80, 
                                      data= g_buf[WRITE_SIZE*i:(WRITE_SIZE*i)+WRITE_SIZE])
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
    buf = bytearray(np.asarray(np.empty(BLOCK_SIZE), np.uint8))
    print ("Reading from DDR")
    while (True):
        f.xem.UpdateTriggerOuts()
        if (f.xem.IsTriggered(0xA0, 0x00)):
            r = f.xem.ReadFromPipeOut(0xA0, data=buf)
            break
    print(buf)
    print ("Read Size: ", r)
    if (g_buf==buf):
        print ("DDR3 read/write worked")
    else:
        print ("Write doesn't match read, DDR3 failed")

writeSDRAM()
readSDRAM()


