from asyncore import write
import opics as op
import re
import os
from opics.utils import universal_sparam_filereader
from pathlib import Path
main_dir = Path(__file__).parent.resolve()
data_dir = main_dir/"example_data\ebeam_taper_te1550"
write_dir = data_dir/"converted_data"

if not os.path.exists(write_dir):
    os.makedirs(write_dir)


enable_actions = {"convert_file_format":False, 
                "consolidate_data": True}

files = [i for i in Path(data_dir).glob("*.dat")]

#component specific parameters
nominal_t = 220e-9
nominal_w = 500e-9
w1_arr = []
w2_arr = []
length_arr = []
nports = 2
component_name = "taper"
main_file_name = "cband_te_taper"
port_name_tag="opt"

for each_file in files:
    temp_data = each_file.parts[-1].split("_")
    w1_arr.append(temp_data[0].split("=")[1])
    w2_arr.append(temp_data[1].split("=")[1])
    length_arr.append(temp_data[2].split("=")[1].split(".")[0])

if(enable_actions["convert_file_format"]):
        for idx in range(len(w1_arr)):
            w1, w2, length = w1_arr[idx], w2_arr[idx], length_arr[idx]
            #Change this string to specify the component data filenames
            filename = f"w1={w1}_w2={w2}_length={length}.dat"
            #open file using opics to convert data to numpy array
            fdata, sdata = universal_sparam_filereader(nports, filename, data_dir)
            #create an empty component and assign data to that component
            temp_component = op.components.componentModel(f=fdata, nports = nports, s=sdata)
            temp_component.write_sparameters(dirpath=write_dir, 
            filename=f"{component_name}_w1={w1}_w2={w2}_length={length}_c.txt",
            f_data=fdata, 
            s_data=sdata,
            port_name_tag=port_name_tag)


if(enable_actions["consolidate_data"]):
    #consolidate the data into a single file
    main_file = open(write_dir/f"{main_file_name}_s_params.txt", "w") # final file
    data_file_objects = {}

    #create data file objects and store them in a dictionary
    for idx in range(len(w1_arr)):
            w1, w2, length = w1_arr[idx], w2_arr[idx], length_arr[idx]

            key = f"{w1}_{w2}_{length}"

            temp_f = open(write_dir/f"{component_name}_w1={w1}_w2={w2}_length={length}_c_gd.txt", "r")
            data_file_objects[key] = temp_f

    keys_arr = list(data_file_objects.keys())

    #write data
    str_data = "test"
    while str_data != "":
        for each_key in keys_arr:
            f_obj = data_file_objects[each_key]
            str_data = f_obj.readline()
            if(str_data==""):
                break
            data_to_write = []
            if(port_name_tag in str_data and each_key==keys_arr[0]):
                #header line
                #str_data = str_data.replace(r"port ", r"opt")
                str_data = str_data.split(",")
                temp_gd = str_data[-1].split(")")[0]
                str_data = ",".join(str_data[:-1])
                str_data = str_data + r", 'wg_width1;wg_width2;wg_length')"+"\n"
                data_to_write.append(str_data)
            #second line
            str_data = f_obj.readline()
            str_data_l = re.split("[,)]",str_data)
            num_datapoints = int(str_data_l[0][1:])
            str_data_l[0] = "("+str(int(str_data_l[0][1:])*len(keys_arr))
            str_data_l[1] = ","+str(int(str_data_l[1])+2)+")"
            str_data = "".join(str_data_l)
            if(each_key==keys_arr[0]):
                data_to_write.append(str_data)

            for _ in range(num_datapoints):
                temp_data = f_obj.readline()
                str_data = [str(op.utils.fromSI(each)) for each in each_key.split("_")] + [temp_data.replace("\n", "\t"+str(temp_gd)+"\n")]           
                data_to_write.append(" ".join(str_data))

            main_file.writelines(data_to_write)
    main_file.close()  
print("done")
  

