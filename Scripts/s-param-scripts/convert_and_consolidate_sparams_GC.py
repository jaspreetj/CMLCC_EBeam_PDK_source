from asyncore import write
import opics as op
import re
import os
from opics.utils import universal_sparam_filereader
from pathlib import Path
main_dir = Path(__file__).parent.resolve()
data_dir = main_dir/"example_data\gc_source"
write_dir = data_dir/"converted_data"

if not os.path.exists(write_dir):
    os.makedirs(write_dir)


enable_actions = {"convert_file_format":False, 
                "consolidate_data": True}


#component specific parameters
nominal_t = 220
nominal_w = 500
thickness_arr = [220, 210, 230]
width_arr = [500, 480, 520]
nports = 2
component_name = "GC_TE1550"
main_file_name = "cband_te_gc"
port_name_tag="opt"

if(enable_actions["convert_file_format"]):
    for width in width_arr:
        for thickness in thickness_arr:
            #Change this string to specify the component data filenames
            filename = f"{component_name}_thickness={thickness} deltaw={width-nominal_w}.txt"

            #open file using opics to convert data to numpy array
            fdata, sdata = universal_sparam_filereader(nports, filename, data_dir)
            #create an empty component and assign data to that component
            temp_component = op.components.componentModel(f=fdata, nports = nports, s=sdata)
            temp_component.write_sparameters(dirpath=write_dir, 
            filename=f"{component_name}_deltat={thickness-nominal_t}_deltaw={width-nominal_w}_c.txt",
            f_data=fdata, 
            s_data=sdata,
            port_name_tag=port_name_tag)


if(enable_actions["consolidate_data"]):
    #consolidate the data into a single file
    main_file = open(write_dir/f"{main_file_name}_s_params.txt", "w") # final file
    data_file_objects = {}

    #create data file objects and store them in a dictionary
    for w in width_arr:
        for t in thickness_arr:
            dw = w-nominal_w
            dt = t-nominal_t

            key = f"{dt}_{dw}"

            temp_f = open(write_dir/f"{component_name}_deltat={dt}_deltaw={dw}_c_gd.txt", "r")
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
                str_data = str_data + r", 'delta_thickness;delta_width')"+"\n"
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
                str_data = [str(int(each)*1e-9) for each in each_key.split("_")] + [temp_data.replace("\n", "\t"+str(temp_gd)+"\n")]           
                data_to_write.append(" ".join(str_data))

            main_file.writelines(data_to_write)
    main_file.close()  
print("done")
  

