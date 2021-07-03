import json
from collections import namedtuple
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
import PyQt5
from PyQt5 import QtWidgets
from qtwidgets import Toggle, AnimatedToggle
import sys

null=0xFF

#Input your values for adc address, trig address for each adc, and then then the mask
ep = namedtuple('ep', 'number addr used downsample_factor trigaddr trigmask')


adc1 = ep(0, 0, True,  1, 0x70, 0x04 )
adc2 = ep(1, 0, True,  1, 0x70, 0x04  )
adc3 = ep(2, 0, True, 1, 0x70, 0x04  )
adc4 = ep(3, 0, True, 1, 0x70, 0x04  )

#to be imported into the driver
adc_list = [adc1, adc2, adc3, adc4]

