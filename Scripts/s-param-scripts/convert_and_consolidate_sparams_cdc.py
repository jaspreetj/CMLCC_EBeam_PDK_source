from asyncore import write
import opics as op
import re
import os
from opics.utils import universal_sparam_filereader
from pathlib import Path

from sqlalchemy import false
main_dir = Path(__file__).parent.resolve()
data_dir = main_dir/"example_data\cdc"
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
dw1_arr = []
dw2_arr = []
gap_arr = []
p_arr=[]
n_arr=[]
s_arr=[]
a_arr=[]
l1_arr=[]
l2_arr=[]
ln_arr = []
nports = 4
component_name = "cdc"
main_file_name = "cband_te_cdc"
port_name_tag="opt"

for each_file in files:
    temp_data = each_file.parts[-1].split(",")
    w1_arr.append(temp_data[0].split("=")[1])
    w2_arr.append(temp_data[1].split("=")[1])
    dw1_arr.append(temp_data[2].split("=")[1])
    dw2_arr.append(temp_data[3].split("=")[1])
    gap_arr.append(temp_data[4].split("=")[1])
    p_arr.append(temp_data[5].split("=")[1])
    n_arr.append(temp_data[6].split("=")[1])
    s_arr.append(temp_data[7].split("=")[1])
    a_arr.append(temp_data[8].split("=")[1])
    l1_arr.append(temp_data[9].split("=")[1])
    l2_arr.append(temp_data[10].split("=")[1])
    ln_arr.append(temp_data[11].split("=")[1].split(".")[0])

if(enable_actions["convert_file_format"]):
        for idx in range(len(w1_arr)):
            w1, w2, dw1, dw2, gap, p, n, s, a, l1, l2, ln = w1_arr[idx], w2_arr[idx], dw1_arr[idx], dw2_arr[idx], gap_arr[idx], p_arr[idx], n_arr[idx], s_arr[idx], a_arr[idx],  l1_arr[idx], l2_arr[idx], ln_arr[idx] 
            #Change this string to specify the component data filenames
            filename = f"w1={w1},w2={w2},dW1={dw1},dW2={dw2},gap={gap},p={p},N={n},s={s},a={a},l1={l1},l2={l2},ln={ln}.dat"
            #open file using opics to convert data to numpy array
            fdata, sdata = universal_sparam_filereader(nports, filename, data_dir)
            #create an empty component and assign data to that component
            temp_component = op.components.componentModel(f=fdata, nports = nports, s=sdata)
            temp_component.write_sparameters(dirpath=write_dir, 
            filename=f"{component_name}_w1={w1}_w2={w2}_dW1={dw1}_dW2={dw2}_gap={gap}_p={p}_N={n}_s={s}_a={a}_c.txt",
            f_data=fdata, 
            s_data=sdata,
            port_name_tag=port_name_tag)


if(enable_actions["consolidate_data"]):
    #consolidate the data into a single file
    main_file = open(write_dir/f"{main_file_name}_s_params.txt", "w") # final file
    data_file_objects = {}

    #create data file objects and store them in a dictionary
    for idx in range(len(w1_arr)):
            w1, w2, dw1, dw2, gap, p, n, s, a, l1, l2, ln = w1_arr[idx], w2_arr[idx], dw1_arr[idx], dw2_arr[idx], gap_arr[idx], p_arr[idx], n_arr[idx], s_arr[idx], a_arr[idx],  l1_arr[idx], l2_arr[idx], ln_arr[idx] 

            key = f"{w1}_{w2}_{dw1}_{dw2}_{gap}_{p}_{n}_{s}_{a}"

            temp_f = open(write_dir/f"{component_name}_w1={w1}_w2={w2}_dW1={dw1}_dW2={dw2}_gap={gap}_p={p}_N={n}_s={s}_a={a}_c_gd.txt", "r")
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
                str_data = str_data + r", 'wg_width1;wg_width2;corrugation_width1;corrugation_width2;gap;grating_period;number_of_periods;sinusoidal;apodization_index')"+"\n"
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
                units_arr = ["nm", "nm","nm","nm","nm","nm","", "", ""]
                keys = each_key.split("_")
                if(keys[-2]=="0"):
                    keys[-2]="false"
                elif(keys[-2]=="1"):
                    keys[-2]="true"
                str_data = [str(op.utils.fromSI(keys[idx]+units_arr[idx])) for idx in range(len(keys))] + [temp_data.replace("\n", "\t"+str(temp_gd)+"\n")]           
                data_to_write.append(" ".join(str_data))

            main_file.writelines(data_to_write)
    main_file.close()  
print("done")
  

