#Examples of the ic dictionaries
ad5453 = {'control_register': (hex)(0x80000041), 'tx_register': (hex)(0x80000001)}

ad7952 = {'control_register': (hex)(0x80000041), 'tx_register': (hex)(0x80000001)}

#an example of an all-encompassing address returning method
def ic_addr(ic, register):
  return (ic[register])
  
# an all-encompassing write method
def ic_write (addr, dataout):
  #data = dev.WriteToPipeIn(addr, dataout)
  exit

#an all-encompassing read method 
def ic_read (addr, datain):
  #data = dev.ReadFromPipeOut(addr, datain)
  #return data
  exit
