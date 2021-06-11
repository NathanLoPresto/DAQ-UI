import json
from collections import namedtuple

null=0xFF

#Input your values for adc address, trig address for each adc, and then then the mask
ep = namedtuple('ep', 'addr trig mask rate')


#Input null if you down want to use an address
adc1 =  ep(0, 0x70, 0x04, 10000000)
adc2 = ep(1, 0x70, 0x04, 10000000)
adc3 = ep(2, 0x70, 0x04, 10000000)
adc4 = ep(3, 0x70, 0x04, 10000000)

#to be imported into the driver
adc_list = [adc1, adc2, adc3, adc4]


