# Renweable Power in the Grid Project 2
# By: Rylan Moore, Andy Neufeld, Vivek Singh

## This repo contains python code to run the full simulation and generate charts. 

All of the useful functions live within 'process.py'. These functions include: 

wind_leap(input.csv) : This function clones Feb 28 to make Feb 29 because the NREL weather data trims leap days. 

clean(input.csv) : This function takes the 30 minute interval solar data and makes it into 5 minute interval data by cloning each datapoint 6 times. 

simulate(input.csv, batt_size, dirty_charge) : This was the initial simulation script. It takes in the raw generation and load data in a csv, the battery size in MWh, and a boolean for if base load should always run when the charge state of the battery is less than 100%. This function is no longer used. 

simulate_new(input.csv, batt_size) : This function is the simulation script used for all results. It takes in the input csv for generation and load and generates "sim_out_new.csv" which contains all dispatch and load met information. 

simulate_base_ao(input, batt) : This function has the base load generation always on. Not used for final results. 

simulate_outage(input, batt, day_out) : Like sim_new but allows the largest wind plant to be taken offline on a day of choice. 

gen_daily_plots(input.csv, day, days, type, perc_geo) : This function geneartes all of the nice matlibplot images for the presentation and paper. Input is the .csv containing all of the stackup info. Day is the day on which to start plotting. Days is the number of days to show. Type allows different size plots to be made based on 'paper' or 'view' for presentation. Finally, perc_geo allows the base load generation stat to be split between the geothermal and hydro facilities based on their proportional sizes. 

## Simulation output files
The .csv files included in the repo are for each of the Scenarios chosen as well as for the Proposed Solution. They are tagged based on the layout of generation resources. 
## Load from project data used in simulation
![image](https://github.com/rylan-moore/CU_Renewable_Project2/assets/70982815/260b69e7-3c9d-4e32-8a08-7ecced9721d7)
## Proposed Solution Plant Locations
![image](https://github.com/rylan-moore/CU_Renewable_Project2/assets/70982815/6b19e0fb-a22e-4e32-a794-205173702532)
## Proposed Solution - Curtailment data
![image](https://github.com/rylan-moore/CU_Renewable_Project2/assets/70982815/45baaff0-eef0-49b3-93f4-939395f311b9)
## Example Matlibplot generated by process.py
![image](https://github.com/rylan-moore/CU_Renewable_Project2/assets/70982815/c615caf4-65bc-46e0-b421-0db2383d2897)





