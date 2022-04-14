global gd_value 
global last_line

#save group delay value from each heading
gd_value = [0]*9 # change 9 to number of files
last_line = True

#function to read all data from given port combination, adds the sweep params to the front ("string"), and group delay at end
def write_line(file, string, open_file):
    line = file.readline()
    if count == 8:
        # if we reach the last line in the last final, set last_line to false to end the while loop
        if not line:
            global last_line 
            last_line = False
            return False
    if line.strip() != '(51,3)' and line:
        if line[0] != '(':
            open_file.write(string + line.strip() + '\t' + str(gd_value[count])+'\n')
        else:
            line_list = line.strip().split(',')
            gd = line_list[-1].strip(')')
            gd_value[count] = gd
            if count == 8:
                #only one file needs to write the header
                open_file.write(','.join([str(item) for item in line_list[:-1]]) + ', "delta_thickness;delta_width")\n')

        return True
    else:
        if count == 8:
            #Adjust given the number of data points (data_points = individual_port_points * number of files)
            f.write('(459, 6)\n')
        return False



f = open("ybranch_s_params_wgd.txt", "w") # final file

widths = [480, 500, 520]
thicknesses = [210, 220, 230]
count = 0


for width in widths:
    for thickness in thicknesses:
        exec('file_'+str(thickness)+str(width) + '= open("./Ybranch_Thickness_{}_width_{}_gd.txt", "r")'.format(thickness, width))

# Loop through each thickness/width for as long as there is still data in the txt files
while last_line:
    count = 0
    for thickness in thicknesses:
        for width in widths:
            exec("while write_line(file_{}{}, '{}e-9\t{}e-9\t', f):\n\tx=1".format(thickness, width,thickness-220, width-500)) # subtract mean to have a 0 statistical mean
            count +=1

for width in widths:
    for thickness in thicknesses:
        exec('file_'+str(thickness)+str(width) + '.close()')
                                                                                                           

f.close()

