# Renweable Power in the Grid Project 2
# By: Rylan Moore, Andy Neufeld, Vivek Singh

## This repo contains python code to run the full simulation and generate charts. 

All of the useful functions live within 'process.py'. These functions include: \

wind_leap(input.csv) : This function clones Feb 28 to make Feb 29 because the NREL weather data trims leap days. \

clean(input.csv) : This function takes the 30 minute interval solar data and makes it into 5 minute interval data by cloning each datapoint 6 times. \

simulate(input.csv, batt_size, dirty_charge) : This was the initial simulation script. It takes in the raw generation and load data in a csv, the battery size in MWh, and a boolean for if base load should always run when the charge state of the battery is less than 100%. This function is no longer used. \

simulate_new(input.csv, batt_size) : This function is the simulation script used for all results. It takes in the input csv for generation and load and generates "sim_out_new.csv" which contains all dispatch and load met information. \

simulate_base_ao(input, batt) : This function has the base load generation always on. Not used for final results. \

simulate_outage(input, batt, day_out) : Like sim_new but allows the largest wind plant to be taken offline on a day of choice. \

gen_daily_plots(input.csv, day, days, type, perc_geo) : This function geneartes all of the nice matlibplot images for the presentation and paper. Input is the .csv containing all of the stackup info. Day is the day on which to start plotting. Days is the number of days to show. Type allows different size plots to be made based on 'paper' or 'view' for presentation. Finally, perc_geo allows the base load generation stat to be split between the geothermal and hydro facilities based on their proportional sizes. \

