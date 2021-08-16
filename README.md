### UI for Servicing General Purpose Operational Amplifiers

**Objective**
***

The objective of the project was to create a UI for a general-purpose operational amplifier centered around electrophysiology experimentation. This includes reading data from a host of ADCs, storing the data into hierarchical data formats, displaying the data in real-time graphing windows and assembling components of the project into a single human-runnable script. In tandem with Dr. Koerner’s ongoing project and the electrophysiology department at the University of Richmond, my codebase and overall design would be open-source, making it free and readily usable for the general public.

***
**How to use this product**
***

This UI is explicitly written for servicing a Xem7310 FPGA board, but can be used for a multitude of OpalKelly Products. With a working bitfile for any OpalKelly board, the only changes needed are endpoint addresses and external hardware changes. Intentionally, the Python script was written as hierarchically as posible with modification in mind. Consult the liscense tab for more information on modification.

***
**Applications**
***

The applications of this project extend deep into the electrophysiology community. While most current hardware used by research teams can cost several thousand dollars, creating an open-source alternative running on a sub $1000 board opens the world of electrophysiology research to smaller Universities and individuals. The subject itself is still in its infancy and creating a more financially inclusive environment for research will propel it into the future.

***
**Methodology/Results(Speed Testing)**
***

Both data coming into the host computer from the ADCs and waveforms written to the DDR3 SDRAM rely on the FrontPanel API's read/write functions. These functions bridge the gap between the Python script and the HDL, and provide fast and reliable transfers between the FPGA and the host computer. By testing the speed of read/write with different transfer lengths, conclusively, the best transfer lengths for the script could be chosen. With multiple tests and a relatively seamless process, results were conclusive and clear that FIFO transfer sizes closest to 16kB yielded that fastest transfer speed.

<img src="https://user-images.githubusercontent.com/78660740/127703939-505e441f-8625-467c-a1ab-aa91157dd2dc.png" width = "400" height = "250">


***
**Acknowledgements**
***

*Special thanks to:* <br />
-Lucas J. Koerner <br />
-University of St. Thomas Engineering Department <br />
-Undergraduate Research Opportunities Program <br />
-Young Scholars Grant <br />
-Coresearchers: Corissa, Ian, Abe & Jake <br />

***
