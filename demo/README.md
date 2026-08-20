
The software and utilites used in this demo are available via Anaconda (https://continuum.io) and include: <br>
<br>
**CMOR** <br>
https://cmor.llnl.gov <br>
https://anaconda.org/conda-forge/cmor <br>
<br>
**xarray** <br>
https://docs.xarray.dev/en/stable <br>
https://anaconda.org/conda-forge/xarray <br> 
<br>
**xcdat** <br>
https://xcdat.readthedocs.io/en/stable <br>
https://anaconda.org/conda-forge/xcdat <br>
<br>
An environment called "MYENVNAME" including the above software can be installed from conda-forge with the following single command:

**conda create -n MYENVNAME -c conda-forge xarray cmor xcdat**

Running the demos, python code reads in the sample data via xarray, generates grid bounds via xcdat, and outputs a demo file using CMOR. The demos must be run with CMOR minimum version 3.2.6 or more recent. To run each demo, all contents in the demo subdirectory (including the /Tables subdirectory) must be saved locally, and a conda environment must be created including CMOR, xarray and xcdat. If python needs to be installed, it too is available via anaconda (https://anaconda.org/conda-forge/python). Once that is done, execute the following: <br>

**demo-global2D**
    
python runCMORdemo_CMAP-V1902.py

**demo-insitu**

python insitu_CMOR_demo.py

**demo-zonalmeans**

python runCMORdemo_zonalmean.py

If you have any difficulties, please contact the obs4MIPs team at obs4mips[dash]panel[at]wcrp[dash]cmip[dot]org

[More details on the process of preparing obs4MIPs compliant data are available in /inputs of this repo.](https://github.com/WCRP-ESMO/obs4MIPs-cmor-tables/blob/master/inputs/README.md)




