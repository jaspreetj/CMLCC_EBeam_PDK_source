from asyncore import write
import opics as op
import re
import os
from opics.utils import universal_sparam_filereader
from pathlib import Path
main_dir = Path(__file__).parent.resolve()
data_dir = main_dir/"example_data\ebeam_terminator_tm1550"
write_dir = data_dir/"converted_data"

if not os.path.exists(write_dir):
    os.makedirs(write_dir)


enable_actions = {"convert_file_format":True, 
                "consolidate_data": False}

files = [i for i in Path(data_dir).glob("*.sparam")]

#component specific parameters
nominal_t = 220e-9
nominal_w = 500e-9
gap_arr = []
Lc_arr = []
nports = 4
component_name = "nanotaper"
main_file_name = "cband_tm_terminator"
port_name_tag="opt"


if(enable_actions["convert_file_format"]):
        for idx in range(len(files)):
            #Change this string to specify the component data filenames
            filename = files[idx]
            w1 = "500nm"
            w2 = "60nm"
            L= "10um"
            #open file using opics to convert data to numpy array
            fdata, sdata = universal_sparam_filereader(nports, filename, data_dir)
            #create an empty component and assign data to that component
            temp_component = op.components.componentModel(f=fdata, nports = nports, s=sdata)
            temp_component.write_sparameters(dirpath=write_dir, 
            filename=f"{main_file_name}_w1={w1}_w2={w2}_L={L}_c.txt",
            f_data=fdata, 
            s_data=sdata,
            port_name_tag=port_name_tag)

