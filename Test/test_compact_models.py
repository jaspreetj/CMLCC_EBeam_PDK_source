# Author: Sean Lam
# Contact: seanlm@student.ubc.ca
# 
# TODO: Add TM mode handling. Requires further testing.
# TODO: Errors from Monte Carlo params still happening in later sims

from lumerical_lumapi import lumapi
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.style.use('ggplot')  # set plotting style
plt.close('all')

intc = lumapi.INTERCONNECT(hide = False)


# List of Old EBeam Models:CMLC EBeam Models
models = {"ebeam_adiabatic_te1550":             "ebeam_cband_te_dc_adiabatic",
          "ebeam_adiabatic_tm1550":             "ebeam_cband_tm_dc_adiabatic",
          "ebeam_bdc_te1550":                   "ebeam_cband_te_bdc",
          "ebeam_bragg_te1550":                 "ebeam_cband_te_bragg",
          "ebeam_crossing4":                    "ebeam_crossing4", # **********NEED SPECIAL CARE
          "ebeam_dc_halfring_straight":         "ebeam_cband_te_dc_halfring_straight",
          "ebeam_dc_te1550":                    "ebeam_cband_te_dc",
          "ebeam_disconnected_te1550":          "ebeam_cband_te_disconnected",
          "ebeam_disconnected_tm1550":          "ebeam_cband_tm_disconnected",
          "ebeam_gc_te1550":                    "ebeam_cband_te_gc",
          "ebeam_gc_tm1550":                    "ebeam_cband_tm_gc",
          "ebeam_splitter_swg_assist_te1550":   "ebeam_cband_te_splitter_swg_assist",
          "ebeam_taper_te1550":                 "ebeam_cband_te_taper",
          "ebeam_terminator_te1550":            "ebeam_cband_te_terminator",
          "ebeam_terminator_tm1550":            "ebeam_cband_tm_terminator",
          "ebeam_wg_integral_1550":             "ebeam_cband_te_wg_strip",
          "ebeam_y_1550":                       "ebeam_cband_te_y_branch",
          "ebeam_y_adiabatic":                  "ebeam_cband_te_y_adiabatic"}


save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),"Test","Verification")
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)

# Marker list for plotting
marker_list = ['o','v','^','<','>','1','2','3','4','s','p','P','*','h','+','X','D']*10

# ONA Settings
c = 299792458 # m/s
center_wavelength = 1550e-9
wavl_range = [1500e-9, 1600e-9]
num_pts = 10000


center_frequency = c/center_wavelength
frequency_range = c/wavl_range[0] - c/wavl_range[1]

for old, new in models.items():
    ### Create verification simulation
    filename = old+"_vs_"+new
    print(filename)
    intc.new()
    intc.save(os.path.join(save_dir, filename+".icp"))
    # Add Monte Carlo params to ensure simulation runs (issue with old EBeam models)
    intc.eval("switchtolayout; deleteall; addproperty('::Root Element', 'MC_uniformity_thickness', 'wafer', 'Matrix');\
          addproperty('::Root Element', 'MC_uniformity_width', 'wafer', 'Matrix'); addproperty('::Root Element', 'MC_grid', 'wafer', 'Number');\
          addproperty('::Root Element', 'MC_resolution_x', 'wafer', 'Number'); addproperty('::Root Element', 'MC_resolution_y', 'wafer', 'Number');\
          addproperty('::Root Element', 'MC_non_uniform', 'wafer', 'Number'); select('::Root Element');")
          
    
    ### Create base level simulation
    intc.addelement(old)
    intc.set("name", "C1")
    ports1 = intc.getports("C1").split("\n")
    
    intc.addelement(old)
    intc.set("name", "C2")
    ports2 = intc.getports("C2").split("\n")
    
    if len(ports1) == len(ports2):
        intc.addelement("Optical Network Analyzer")
        intc.set("name", "ONA1")
        intc.set("center frequency", center_frequency)
        intc.set("frequency range", frequency_range)
        intc.set("number of points", num_pts)
        intc.set("number of input ports", len(ports1) - 1)
        if "tm" in filename:
            intc.set("orthogonal identifier", 2)
        else:
            intc.set("orthogonal identifier", 1)
        
        intc.addelement("Optical Network Analyzer")
        intc.set("name", "ONA2")
        intc.set("center frequency", center_frequency)
        intc.set("frequency range", frequency_range)
        intc.set("number of points", num_pts)
        intc.set("number of input ports", len(ports2) - 1)
        if "tm" in filename:
            intc.set("orthogonal identifier", 2)
        else:
            intc.set("orthogonal identifier", 1)
        
        for i in range(0, len(ports1)):
            # Disconnect all connections
            intc.switchtolayout()
            intc.disconnect("C1")
            intc.disconnect("C2")
            
            # Connect component 1 to ONA 1 in various permutations
            intc.connect("C1", ports1[i], "ONA1", "output")
            k = 1
            port_mapping1 = {}
            for j in range(0, len(ports1)):
                if j != i:
                    intc.connect("C1", ports1[j], "ONA1", "input "+str(k))
                    port_mapping1["input "+str(k)] = ports1[j]
                    k=k+1
            
            # Connect component 2 to ONA 2 in various permutations
            intc.connect("C2", ports2[i], "ONA2", "output")
            k = 1
            port_mapping2 = {}
            for j in range(0, len(ports2)):
                if j != i:
                    intc.connect("C2", ports2[j], "ONA2", "input "+str(k))
                    port_mapping2["input "+str(k)] = ports2[j]
                    k=k+1
            
            # Run sim
            intc.run()
            
            # Extract data
            for k in range(1, len(ports1)):
                wavl1 = intc.getresult("ONA1", "input "+str(k)+"/mode 1/gain")["wavelength"]
                if "tm" in filename:
                    gain1 = intc.getresult("ONA1", "input "+str(k)+"/mode 1/gain")["'TM' gain (dB)"]
                    angle1 = intc.getresult("ONA1", "input "+str(k)+"/mode 1/angle")["'TM' angle (rad)"]
                else:
                    gain1 = intc.getresult("ONA1", "input "+str(k)+"/mode 1/gain")["'TE' gain (dB)"]
                    angle1 = intc.getresult("ONA1", "input "+str(k)+"/mode 1/angle")["'TE' angle (rad)"]
                
                wavl2 = intc.getresult("ONA2", "input "+str(k)+"/mode 1/gain")["wavelength"]
                if "tm" in filename:
                    gain2 = intc.getresult("ONA2", "input "+str(k)+"/mode 1/gain")["'TM' gain (dB)"]
                    angle2 = intc.getresult("ONA2", "input "+str(k)+"/mode 1/angle")["'TM' angle (rad)"]
                else:
                    gain2 = intc.getresult("ONA2", "input "+str(k)+"/mode 1/gain")["'TE' gain (dB)"]
                    angle2 = intc.getresult("ONA2", "input "+str(k)+"/mode 1/angle")["'TE' angle (rad)"] 
                
                fig1 = plt.figure(figsize=(8, 6))
                ax1 = fig1.add_subplot(111)
                ax1.plot(wavl1, gain1, label="Old", marker=marker_list[0])
                ax1.plot(wavl2, gain2, label="New", marker=marker_list[1])
                ax1.set_xlabel("Wavelength")
                ax1.set_ylabel("Gain")
                ax1.grid('on')
                ax1.legend()
                fig1.savefig(os.path.join(save_dir,filename+"_gain_"+ports1[i]+"-"+port_mapping1["input "+str(k)] +"_"+ports2[i]+"-"+port_mapping2["input "+str(k)] +'.png'))
                
                fig2 = plt.figure(figsize=(8, 6))
                ax2 = fig2.add_subplot(111)
                ax2.plot(wavl1, angle1, label="Old", marker=marker_list[0])
                ax2.plot(wavl2, angle2, label="New", marker=marker_list[1])
                ax2.set_xlabel("Wavelength")
                ax2.set_ylabel("Angle")
                ax2.grid('on')
                ax2.legend()
                fig1.savefig(os.path.join(save_dir,filename+"_angle_"+ports1[i]+"-"+port_mapping1["input "+str(k)] +"_"+ports2[i]+"-"+port_mapping2["input "+str(k)] +'.png'))
                
    else:
        print("Issue with "+old+" model and "+new+" model... Ports not same...")
        
        
    
    
    
    