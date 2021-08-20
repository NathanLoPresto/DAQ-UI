
***
# UI for Servicing General Purpose Operational Amplifiers

The objective of the project was to create a UI for a general-purpose operational amplifier centered around electrophysiology experimentation. This includes reading data from a host of ADCs, storing the data into hierarchical data formats, displaying the data in real-time graphing windows and assembling components of the project into a single human-runnable script. In tandem with Dr. Koerner’s ongoing project and the electrophysiology department at the University of Richmond, my codebase and overall design would be open-source, making it free and readily usable for the general public.

Initially appeared on
[gist](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2). But the page cannot open anymore so that is why I have moved it here.

## Getting Started

This UI is explicitly written for servicing a Xem7310 FPGA board, but can be used for a multitude of OpalKelly Products. With a working bitfile for any OpalKelly board, the only changes needed are endpoint addresses and external hardware changes. Intentionally, the Python script was written as hierarchically as posible with modification in mind. Consult the liscense tab for more information on modification.

### Prerequisites

Requirements for the software and other tools to build, test and push 
- [Example 1](https://www.example.com)
- [Example 2](https://www.example.com)

### Installing

You will need several packages to run the software, all can be done with a "pip install"

Following commands need to be run:

    pip install PyQt5
    pip install scipy
    pip install pyqtgraph
    pip install numpy
    pip install json
    pip install h5py
    pip install platform




## Applications

The applications of this project extend deep into the electrophysiology community. While most current hardware used by research teams can cost several thousand dollars, creating an open-source alternative running on a sub $1000 board opens the world of electrophysiology research to smaller Universities and individuals. The subject itself is still in its infancy and creating a more financially inclusive environment for research will propel it into the future.

### Speed testing(Transfer Size)

Both data coming into the host computer from the ADCs and waveforms written to the DDR3 SDRAM rely on the FrontPanel API's read/write functions. These functions bridge the gap between the Python script and the HDL, and provide fast and reliable transfers between the FPGA and the host computer. By testing the speed of read/write with different transfer lengths, conclusively, the best transfer lengths for the script could be chosen. With multiple tests and a relatively seamless process, results were conclusive and clear that FIFO transfer sizes closest to 16kB yielded that fastest transfer speed.


    <img src="https://user-images.githubusercontent.com/78660740/127703939-505e441f-8625-467c-a1ab-aa91157dd2dc.png" width = "400" height = "250">

### Speed test(Window Updates)

Checks if the best practices and the right coding style has been used.

    Give an example

## Deployment

Add additional notes to deploy this on a live system

## Authors

  - **Nathan LoPresto** - *Provided README Template* -
    [Nathan LoPresto](https://github.com/NathanLoPresto)


## License

This project is licensed under the [MIT License](LICENSE.md)
Creative Commons License - see the [LICENSE.md](LICENSE.md) file for
details

## Acknowledgments

    -Lucas J. Koerner
    -University of St. Thomas Engineering Department 
    -Undergraduate Research Opportunities Program
    -Young Scholars Grant
    -Coresearchers: Corissa, Ian, Abe & Jake