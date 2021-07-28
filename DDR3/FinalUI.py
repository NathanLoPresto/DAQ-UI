from fpga import FPGA 

#Initialize the FPGA for script to run 
if __name__ == "__main__":

    f = FPGA(bitfile = 'pipe1.bit')
    if (False == f.init_device()):
        raise SystemExit
            # reset PLL 
