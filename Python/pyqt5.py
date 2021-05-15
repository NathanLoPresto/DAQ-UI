import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
import numpy as np
import matplotlib.pyplot as plt
#Imports for time, fpga, and matplotlib
import time
import numpy
import random
from threading import Thread
#from drivers.utils import rev_lookup, bin, test_bit, twos_comp, gen_mask
import matplotlib.animation as animation
start_time= time.time()

def greeting():
  os.system ('python simulator.py')

def ex():
    sys.exit()
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle('OPAMP GUI')
layout = QVBoxLayout()

btn = QPushButton('Run software')
btn.clicked.connect(greeting)# import main loop into here to run inside app
bt = QPushButton('Exit')
bt.clicked.connect(ex)  # Exit button can be pressed to exit the program

layout.addWidget(btn)
layout.addWidget(bt)
msg = QLabel('')
layout.addWidget(msg)
window.setLayout(layout)
window.setStyleSheet("background-color: grey;")
window.setGeometry(500,200,500,200)
window.show()
sys.exit(app.exec_())

