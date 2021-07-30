### UI for Servicing General Purpose Operational Amplifiers

**Objective**
***
The objective of the project was to create a UI for a general-purpose operational amplifier centered around electrophysiology experimentation. This includes reading data from a host of ADCs, storing the data into hierarchical data formats, displaying the data in real-time graphing windows and assembling components of the project into a single human-runnable script. In tandem with Dr. Koerner’s ongoing project and the electrophysiology department at the University of Richmond, my codebase and overall design would be open-source, making it free and readily usable for the general public.
***
**Applications**
***
The applications of this project extend deep into the electrophysiology community. While most current hardware used by research teams can cost several thousand dollars, creating an open-source alternative running on a sub $1000 board opens the world of electrophysiology research to smaller Universities and individuals. The subject itself is still in its infancy and creating a more financially inclusive environment for research will propel it into the future.
***
**Methodology/Results(Speed Testing)**
***
When conducting speed tests (below), the best way to automate the process was with a Python script cycling though transfer sizes and returning transfer time elapsed. This value could divide the returned transfer size and write a speed in MB/s to a CSV file. With multiple tests and a relatively seamless process, results were conclusive and clear that FIFO transfer sizes closest to 16kB yielded that fastest transfer speed.

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
