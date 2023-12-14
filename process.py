import os
import csv
import pandas as pd
from datetime import datetime
import statistics

import matplotlib.pyplot as plot

def wind_leap(input):
    tmpFile = "tmp.csv"
    with open(input, "r") as file, open(tmpFile, "w") as outFile:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(outFile, delimiter=',')
        header = next(reader)
        writer.writerow(header)
        cache = []
        row_i = 1
        for row in reader:
                # print(row)
            # for i in range(6):
                if row_i > 16704 and row_i < 16993:
                    for col in row:
                        cache.append(col.lower())
                colValues = []
                for col in row:
                    colValues.append(col.lower())
                writer.writerow(colValues)
                
                if row_i == 16992:
                    # print(cache)
                    for i in range(0,288*2,2) :
                        leapValues = []
                        leapValues.append(cache[i])
                        leapValues.append(cache[i+1])
                        # print(leapValues)
                        writer.writerow(leapValues)
                row_i += 1
        outFile.close()
        tmpFile.close()

def clean(input):
    tmpFile = "tmp.csv"
    with open(input, "r") as file, open(tmpFile, "w") as outFile:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(outFile, delimiter=',')
        header = next(reader)
        writer.writerow(header)
        for row in reader:
            for i in range(6):
                colValues = []
                for col in row:
                    colValues.append(col.lower())
                writer.writerow(colValues)
    os.close(outFile)
    os.close(tmpFile)


c_time = 0
c_load = 1
c_wind = 2
c_solar = 3
c_db = 6
c_batt = 11
c_lfg = 9

#output
# 

#Runs 5 minute dispatch steps to check all source generation and see results and stackup
def simulate(input, batt, dirty_charge):
    tmpFile = "sim_out.csv"
    prev_batt = batt/2 #MWh start battery off half full
    batt_cap = batt #MWh
    with open(input, "r") as file, open(tmpFile, "w") as outFile:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(outFile, delimiter=',')        
        header = next(reader)
        top = ["time", "load MW", "wind MW", "solar MW", "lfg MWa", "BATT fuel MWh", "Batt Load MW", "Curtail renew MW", "Hundred T/F", "Demand met T/F"]
        writer.writerow(top)
        # writer.writerow("time, load, wind, solar, lfg, Batt fuel, Batt load, Curtail, Hundred (T/F), met (T/F)")
        for row in reader:
            try:
                time = float(row[c_time])
                load = float(row[c_load])
                wind = float(row[c_wind])
                solar = float(row[c_solar])
                diff_b = float(row[c_db])
                batt = row[c_batt]
                lfg = float(row[c_lfg])
            except:
                break
            print(time, end="")
            excess = 0
            if diff_b < 0: #excess renewable generation
                Hundred = True
                if prev_batt < batt_cap: #if we can put more in the battery
                    next_batt = prev_batt + -1*diff_b/12 #add the excess in MWh
                    batt_load = diff_b #the instant load on the battery
                    if dirty_charge:
                        next_batt = prev_batt + -1*diff_b/12 +lfg/12 #add the excess in MWh
                        Hundred = False
                    excess = 0
                    if next_batt > batt_cap:
                        excess = next_batt - batt_cap
                        next_batt = batt_cap
                else:
                    batt_load = 0
                    excess = diff_b
                met = True
                
            if diff_b > 0: #not enough renewable generation
                excess = 0 #excess renewable production
                if not dirty_charge:
                    if prev_batt * 12 > diff_b: #try to use up the battery MW*5min
                        batt_load = diff_b
                        next_batt = prev_batt - diff_b / 12 
                        Hundred = True
                        
                        met = True
                    else: #need to try and use LFG
                        cover = diff_b - prev_batt / 12 - lfg
                        batt_load = prev_batt / 12 #TODO calculate this correctly.
                        next_batt = 0
                        print(" %f - %f - %f" % (diff_b, cover, lfg), end="")
                        if cover < 0: #LFG capacity covered the error
                            Hundred = False
                            met = True  
                        else: #LFG did not cover it!
                            Hundred = False
                            met = False
                if dirty_charge:
                    cover = diff_b - lfg
                    if cover < 0:
                        next_batt = prev_batt
                        met = True
                        Hundred = False
                    else:
                        if prev_batt * 12 > cover:
                            batt_load = cover
                            next_batt = prev_batt - cover / 12
                            Hundred = False
                            met = True
                        else:
                            met = False
                            Hundred = False
                            next_batt = 0
            print("")
            
            #need to print out the row
            output = []
            output.append(time)
            output.append(load)
            output.append(wind)
            output.append(solar)
            output.append(lfg)
            output.append(next_batt)
            output.append(batt_load)
            output.append(excess)
            output.append(int(Hundred))
            output.append(int(met))

            # output = ("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (time, load, wind, solar, lfg, next_batt, batt_load, excess, Hundred, met))
            writer.writerow(output)
            prev_batt = next_batt


c_time = 0
c_load = 1
c_base = 2
c_wind = 4
c_solar = 3
c_solar_two = 5
c_wind_two = 6



#Runs 5 minute dispatch steps to check all source generation and see results and stackup
def simulate_new(input, batt):
    dirty_charge = True
    tmpFile = "sim_out_new.csv"
    prev_batt = batt/2 #MWh start battery off half full
    batt_cap = batt #MWh
    with open(input, "r") as file, open(tmpFile, "w") as outFile:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(outFile, delimiter=',')        
        header = next(reader)
        top = ["time", "load MW", "wind MW", "solar MW", "lfg MWa", "BATT fuel MWh", "Batt Load MW", 
               "Curtail renew MW","Base dispatched", "Solar dispatched", "Wind dispatched", 
               "Battery Dispatched", "Hundred T/F", "Demand met T/F"]
        writer.writerow(top)
        # writer.writerow("time, load, wind, solar, lfg, Batt fuel, Batt load, Curtail, Hundred (T/F), met (T/F)")
        for row in reader:
            try:
                time = float(row[c_time])
                load = float(row[c_load])
                wind = float(row[c_wind])  + float(row[c_wind_two])#add other plants here
                solar = float(row[c_solar])/2 + float(row[c_solar_two])#add other plants here
                # diff_b = float(row[c_db])
                # batt = row[c_batt]
                lfg = float(row[c_base])
            except:
                print("Error parsing rows of input file")
                break
            solar_stack = 0
            batt_stack = 0
            base_stack = 0
            wind_stack = 0
            print(time, end="")
            diff_b = load - wind - solar
            excess = 0
            if diff_b < 0: #excess renewable generation
                Hundred = True
                base_stack = 0
                batt_stack = 0
                r_total = solar + wind
                wind_stack = load * (wind/r_total)
                solar_stack = load * (solar/r_total)
                
                # print("Excess")
                if prev_batt < batt_cap: #if we can put more in the battery
                    next_batt = prev_batt + -1*diff_b/12 #add the excess in MWh
                    batt_load = diff_b #the instant load on the battery
                    batt_stack = diff_b
                    r_left = (wind - wind_stack) + (solar - solar_stack)
                    s_left = solar - solar_stack
                    w_left = wind - wind_stack
                    wind_stack += -diff_b * (w_left / r_left)
                    solar_stack += -diff_b * (s_left/ r_left)
                    base_stack = lfg
                    if dirty_charge:
                        next_batt = prev_batt + -1*diff_b/12 +lfg/12 #add the excess in MWh
                        batt_stack -= lfg #also need to figure in charging from base load
                        Hundred = True
                    excess = 0
                    if next_batt > batt_cap:
                        excess = next_batt - batt_cap
                        next_batt = batt_cap
                        solar_stack -= excess/3
                        wind_stack -= excess/3
                        base_stack -= excess/3
                else:
                    batt_load = 0
                    next_batt = prev_batt
                    excess = -diff_b
                met = True
                
            if diff_b > 0: #not enough renewable generation
                excess = 0 #excess renewable production
                wind_stack = wind
                solar_stack = solar
                if not dirty_charge:
                    if prev_batt * 12 > diff_b: #try to use up the battery MW*5min
                        batt_load = diff_b
                        next_batt = prev_batt - diff_b / 12 
                        Hundred = True
                        
                        met = True
                    else: #need to try and use LFG
                        cover = diff_b - prev_batt / 12 - lfg
                        batt_load = prev_batt / 12 #TODO calculate this correctly.
                        next_batt = 0
                        print(" %f - %f - %f" % (diff_b, cover, lfg), end="")
                        if cover < 0: #LFG capacity covered the error
                            Hundred = True
                            met = True  
                        else: #LFG did not cover it!
                            Hundred = True
                            met = False
                if dirty_charge:
                    cover = diff_b - lfg
                    if cover < 0:
                        base_stack = diff_b
                        next_batt = prev_batt
                        met = True
                        Hundred = True
                    else:
                        base_stack = lfg
                        if prev_batt * 12 > cover:
                            batt_load = cover
                            batt_stack = cover
                            next_batt = prev_batt - cover / 12
                            Hundred = False
                            met = True
                        else:
                            batt_stack = 0
                            met = False
                            Hundred = True
                            next_batt = 0
            print("")
            
            #need to print out the row
            output = []
            output.append(time)
            output.append(load)
            output.append(wind)
            output.append(solar)
            output.append(lfg)
            output.append(next_batt)
            output.append(batt_load)
            output.append(excess)
            output.append(base_stack)
            output.append(solar_stack)
            output.append(wind_stack)
            output.append(batt_stack)
            output.append(int(Hundred))
            output.append(int(met))

            # output = ("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (time, load, wind, solar, lfg, next_batt, batt_load, excess, Hundred, met))
            writer.writerow(output)
            prev_batt = next_batt


def simulate_base_ao(input, batt):
    dirty_charge = True
    tmpFile = "sim_out_new.csv"
    prev_batt = batt/2 #MWh start battery off half full
    batt_cap = batt #MWh
    with open(input, "r") as file, open(tmpFile, "w") as outFile:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(outFile, delimiter=',')        
        header = next(reader)
        top = ["time", "load MW", "wind MW", "solar MW", "lfg MWa", "BATT fuel MWh", "Batt Load MW", 
               "Curtail renew MW","Base dispatched", "Solar dispatched", "Wind dispatched", 
               "Battery Dispatched", "Hundred T/F", "Demand met T/F"]
        writer.writerow(top)
        # writer.writerow("time, load, wind, solar, lfg, Batt fuel, Batt load, Curtail, Hundred (T/F), met (T/F)")
        for row in reader:
            try:
                time = float(row[c_time])
                load = float(row[c_load])
                wind = float(row[c_wind]) #add other plants here
                solar = float(row[c_solar]) + float(row[c_solar_two])#add other plants here
                # diff_b = float(row[c_db])
                # batt = row[c_batt]
                lfg = float(row[c_base])
            except:
                print("Error parsing rows of input file")
                break
            solar_stack = 0
            batt_stack = 0
            base_stack = lfg
            load = load - lfg
            wind_stack = 0
            print(time, end="")
            diff_b = load - wind - solar
            excess = 0
            if diff_b < 0: #excess renewable generation
                Hundred = True
                # base_stack = 0
                batt_stack = 0
                r_total = solar + wind
                wind_stack = load * (wind/r_total)
                solar_stack = load * (solar/r_total)
                
                # print("Excess")
                if prev_batt < batt_cap: #if we can put more in the battery
                    next_batt = prev_batt + -1*diff_b/12 #add the excess in MWh
                    batt_load = diff_b #the instant load on the battery
                    batt_stack = diff_b
                    r_left = (wind - wind_stack) + (solar - solar_stack)
                    s_left = solar - solar_stack
                    w_left = wind - wind_stack
                    wind_stack += -diff_b * (w_left / r_left)
                    solar_stack += -diff_b * (s_left/ r_left)
                    # base_stack = lfg
                    if dirty_charge:
                        next_batt = prev_batt + -1*diff_b/12 #add the excess in MWh
                        # batt_stack -= lfg #also need to figure in charging from base load
                        Hundred = True
                    excess = 0
                    if next_batt > batt_cap:
                        excess = next_batt - batt_cap
                        next_batt = batt_cap
                        solar_stack -= excess/2
                        wind_stack -= excess/2
                        # base_stack -= excess/3
                else:
                    batt_load = 0
                    next_batt = prev_batt
                    excess = -diff_b
                met = True
                
            if diff_b > 0: #not enough renewable generation
                excess = 0 #excess renewable production
                wind_stack = wind
                solar_stack = solar
                
                if dirty_charge:
                    cover = diff_b
                    if cover < 0:
                        base_stack = diff_b
                        next_batt = prev_batt
                        met = True
                        Hundred = True
                    else:
                        base_stack = lfg
                        if prev_batt * 12 > cover:
                            batt_load = cover
                            batt_stack = cover
                            next_batt = prev_batt - cover / 12
                            Hundred = False
                            met = True
                        else:
                            batt_stack = 0
                            met = False
                            Hundred = True
                            next_batt = 0
            print("")
            
            #need to print out the row
            output = []
            load += lfg #nee to factor base load back in lol
            output.append(time)
            output.append(load)
            output.append(wind)
            output.append(solar)
            output.append(lfg)
            output.append(next_batt)
            output.append(batt_load)
            output.append(excess)
            output.append(base_stack)
            output.append(solar_stack)
            output.append(wind_stack)
            output.append(batt_stack)
            output.append(int(Hundred))
            output.append(int(met))

            # output = ("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (time, load, wind, solar, lfg, next_batt, batt_load, excess, Hundred, met))
            writer.writerow(output)
            prev_batt = next_batt

def simulate_outage(input, batt, day_out):
    dirty_charge = True
    tmpFile = "sim_out_new.csv"
    prev_batt = batt/2 #MWh start battery off half full
    batt_cap = batt #MWh
    with open(input, "r") as file, open(tmpFile, "w") as outFile:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(outFile, delimiter=',')        
        header = next(reader)
        top = ["time", "load MW", "wind MW", "solar MW", "lfg MWa", "BATT fuel MWh", "Batt Load MW", 
               "Curtail renew MW","Base dispatched", "Solar dispatched", "Wind dispatched", 
               "Battery Dispatched", "Hundred T/F", "Demand met T/F"]
        writer.writerow(top)
        # writer.writerow("time, load, wind, solar, lfg, Batt fuel, Batt load, Curtail, Hundred (T/F), met (T/F)")
        i = 1
        for row in reader:
            try:
                if i > day_out*288 and i < (day_out+1)*(288):
                    # print("wind out", end="")
                    time = float(row[c_time])
                    load = float(row[c_load])
                    wind = float(row[c_wind_two])#add other plants here float(row[c_wind])  #+ 
                    solar = float(row[c_solar])/2 + float(row[c_solar_two])#add other plants here
                    # diff_b = float(row[c_db])
                    # batt = row[c_batt]
                    lfg = float(row[c_base])
                else:
                    time = float(row[c_time])
                    load = float(row[c_load])
                    wind = float(row[c_wind])  + float(row[c_wind_two])#add other plants here
                    solar = float(row[c_solar])/2 + float(row[c_solar_two])#add other plants here
                    # diff_b = float(row[c_db])
                    # batt = row[c_batt]
                    lfg = float(row[c_base])
            except:
                print("Error parsing rows of input file")
                break
            i+= 1
            solar_stack = 0
            batt_stack = 0
            base_stack = 0
            wind_stack = 0
            print(time, end="")
            diff_b = load - wind - solar
            excess = 0
            if diff_b < 0: #excess renewable generation
                Hundred = True
                base_stack = 0
                batt_stack = 0
                r_total = solar + wind
                wind_stack = load * (wind/r_total)
                solar_stack = load * (solar/r_total)
                
                # print("Excess")
                if prev_batt < batt_cap: #if we can put more in the battery
                    next_batt = prev_batt + -1*diff_b/12 #add the excess in MWh
                    batt_load = diff_b #the instant load on the battery
                    batt_stack = diff_b
                    r_left = (wind - wind_stack) + (solar - solar_stack)
                    s_left = solar - solar_stack
                    w_left = wind - wind_stack
                    wind_stack += -diff_b * (w_left / r_left)
                    solar_stack += -diff_b * (s_left/ r_left)
                    base_stack = lfg
                    if dirty_charge:
                        next_batt = prev_batt + -1*diff_b/12 +lfg/12 #add the excess in MWh
                        batt_stack -= lfg #also need to figure in charging from base load
                        Hundred = True
                    excess = 0
                    if next_batt > batt_cap:
                        excess = next_batt - batt_cap
                        next_batt = batt_cap
                        solar_stack -= excess/3
                        wind_stack -= excess/3
                        base_stack -= excess/3
                else:
                    batt_load = 0
                    next_batt = prev_batt
                    excess = -diff_b
                met = True
                
            if diff_b > 0: #not enough renewable generation
                excess = 0 #excess renewable production
                wind_stack = wind
                solar_stack = solar
                if not dirty_charge:
                    if prev_batt * 12 > diff_b: #try to use up the battery MW*5min
                        batt_load = diff_b
                        next_batt = prev_batt - diff_b / 12 
                        Hundred = True
                        
                        met = True
                    else: #need to try and use LFG
                        cover = diff_b - prev_batt / 12 - lfg
                        batt_load = prev_batt / 12 #TODO calculate this correctly.
                        next_batt = 0
                        print(" %f - %f - %f" % (diff_b, cover, lfg), end="")
                        if cover < 0: #LFG capacity covered the error
                            Hundred = True
                            met = True  
                        else: #LFG did not cover it!
                            Hundred = True
                            met = False
                if dirty_charge:
                    cover = diff_b - lfg
                    if cover < 0:
                        base_stack = diff_b
                        next_batt = prev_batt
                        met = True
                        Hundred = True
                    else:
                        base_stack = lfg
                        if prev_batt * 12 > cover:
                            batt_load = cover
                            batt_stack = cover
                            next_batt = prev_batt - cover / 12
                            Hundred = False
                            met = True
                        else:
                            batt_stack = 0
                            met = False
                            Hundred = True
                            next_batt = 0
            print("")
            
            #need to print out the row
            output = []
            output.append(time)
            output.append(load)
            output.append(wind)
            output.append(solar)
            output.append(lfg)
            output.append(next_batt)
            output.append(batt_load)
            output.append(excess)
            output.append(base_stack)
            output.append(solar_stack)
            output.append(wind_stack)
            output.append(batt_stack)
            output.append(int(Hundred))
            output.append(int(met))

            # output = ("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (time, load, wind, solar, lfg, next_batt, batt_load, excess, Hundred, met))
            writer.writerow(output)
            prev_batt = next_batt


def gen_daily_plots(input, day, days, type, perc_geo):
    day_s = day
    # days = 1
    if days > 366 or day < 1 or day > 365 or day+days > 367:
        print("Usage [csv] [day 1-365] [days to display 1-365]")
        return
    day = (day -1) * 288
    with open(input, "r") as file:

        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        stack = {
            "Solar": [],
            "Wind": [],
            "Base": [],
            "hydro": [],
            "Battery": [],
        }
        time = []
        load = []
        b_fuel = []
        limit = []
        i = 1
        for row in reader:
            if i >= day and i <= day+288*days:
                load.append(float(row[1]))
                time.append((i-day)*5/60)
                b_fuel.append(float(row[5]))
                limit.append(float(row[7]))
                stack["Solar"].append(max(float(row[9]), 0))
                stack["Wind"].append(float(row[10]))
                stack["Base"].append(float(row[8])*perc_geo)
                stack["hydro"].append(float(row[8])*(1-perc_geo))
                stack["Battery"].append(max(float(row[11]), 0))
                # stack["Battery"].append(float(row[11]))
            elif i > day:
                break
            # else:
            i += 1
        # dataFrame   = pd.DataFrame(stack, index=time)
        # #Draw an area plot for the DataFrame data
        # load, ax1 = pd.DataFrame(load, index=time)
        # # batt = pd.DataFrame(b_fuel, index=time)

        # # plt.plot(df['A'])
        # fig, ax1 = plot.plot(load, "b--")
        # ax2 = ax1.twiny()
        # plot.stackplot(time, stack["Base"], stack["Battery"], stack["Solar"], stack["Wind"], labels=['Geothermal', 'Battery', 'Solar', 'Wind'])
        # # plot.plot(b_fuel, secondary_y = True)
        # # plot.twiny(b_fuel)
        # plot.legend(loc='upper left')
        # plot.title("Day %d" % (day/288))
        # # dataFrame.plot(kind='area', stacked=True)
        # # load.plot(kind='line')
        if type == "paper":
            fig, ax1 = plot.subplots(figsize=(8, 5))
        if type == "view":
            fig, ax1 = plot.subplots(figsize=(16, 8))
        # fig, (ax1, ax2) = plot.subplots(2,1,figsize=(6, 8))
        
        # ax2a = ax2.twinx()

        ax1.plot(time, load, "b", label='Load MW')
        if perc_geo != 1:
            pal = ["#FF8433", "#2A3FD0", "#FFBD33", "#21C0D3", "#CA3030", "#F91414" ]
            ax1.stackplot(time, stack["Base"],stack["hydro"], stack["Solar"], stack["Wind"], stack["Battery"], limit, colors = pal,  labels=['Geothermal MW','Hydro MW', 'Solar MW', 'Wind MW','Battery MW', 'Renewable Curtail MW'])           
        elif statistics.fmean(stack["Base"]) != 0 and statistics.fmean(stack["Battery"]) != 0:
            pal = ["#FF8433", "#FFBD33", "#21C0D3", "#CA3030", "#F91414" ]
            ax1.stackplot(time, stack["Base"], stack["Solar"], stack["Wind"], stack["Battery"], limit, colors = pal,  labels=['Geothermal MW', 'Solar MW', 'Wind MW','Battery MW', 'Renewable Curtail MW'])
        elif statistics.fmean(stack["Base"]) == 0 and statistics.fmean(stack["Battery"]) != 0:
            pal = [ "#FFBD33", "#21C0D3", "#CA3030", "#F91414" ]
            ax1.stackplot(time, stack["Solar"], stack["Wind"], stack["Battery"], limit, colors = pal,  labels=['Solar MW', 'Wind MW','Battery MW', 'Renewable Curtail MW'])  
        elif statistics.fmean(stack["Base"]) != 0 and statistics.fmean(stack["Battery"]) == 0:
            pal = ["#FF8433", "#FFBD33", "#21C0D3", "#F91414" ]
            ax1.stackplot(time, stack["Base"], stack["Solar"], stack["Wind"], limit, colors = pal,  labels=['Geothermal MW', 'Solar MW', 'Wind MW', 'Renewable Curtail MW'])  
        else:
            pal = [ "#FFBD33", "#21C0D3",  "#F91414" ]
            ax1.stackplot(time, stack["Solar"], stack["Wind"],  limit, colors = pal,  labels=['Solar MW', 'Wind MW', 'Renewable Curtail MW'])         
        
        if statistics.fmean(b_fuel) != 0:
            ax1a = ax1.twinx()
            ax1a.plot(time, b_fuel, "g--", label='Battery Charge MWh')
            ax1a.set_ylabel("MWh")
            ax1a.axis([0,24*days,0,max(b_fuel)+50])
        children = ax1.get_children()
        if perc_geo != 1:
            children[5].set_alpha(0.2)
        elif statistics.fmean(stack["Base"]) != 0 and statistics.fmean(stack["Battery"]) != 0:
            children[4].set_alpha(0.2)
        elif statistics.fmean(stack["Base"]) == 0 and statistics.fmean(stack["Battery"]) != 0:
            children[3].set_alpha(0.2)
        elif statistics.fmean(stack["Base"]) != 0 and statistics.fmean(stack["Battery"]) == 0:
            children[3].set_alpha(0.2)
        else:
            children[2].set_alpha(0.2)
        # ax2.stackplot(time, limit, labels=["Renewable Curtail MW"])
        # ax1.set_xlabel("Date")
        # ax1.set_ylabel("Temperature (Celsius °)", color=COLOR_TEMPERATURE, fontsize=14)
        # ax1.tick_params(axis="y", labelcolor=COLOR_TEMPERATURE)

        # ax2.set_ylabel("Price ($)", color=COLOR_PRICE, fontsize=14)
        # ax2.tick_params(axis="y", labelcolor=COLOR_PRICE)
        fig.legend(loc='upper center', ncol = 3, bbox_to_anchor=(0.5,0.95), fancybox=True,shadow=True) # 
        fig.tight_layout()
        ax1.set_xlabel("Hour")
        ax1.set_ylabel("MW")
        ax1.grid(axis = 'y', linestyle='--', alpha=0.3)
        
        # ax2.set_xlabel("Hour of day")
        # ax2.set_ylabel("MW")
        # ax1.autoscale()

        day_num = str(day_s)
        day_num.rjust(3 + len(day_num), '0')
        
        day_end = str(day_s+days-1)
        day_end.rjust(3 + len(day_num), '0')
        # Initialize year
        year = "2012"
        # converting to date
        res = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%m-%d-%Y")
        res_end = datetime.strptime(year + "-" + day_end, "%Y-%j").strftime("%m-%d-%Y")

        
        # fig.autofmt_xdate()
        # fig.tight_layout(h_pad=2)
        fig.suptitle("Curve on day(s) %s through %s" % (str(res), str(res_end)), fontsize=15)
        fig.subplots_adjust(top=0.85)
        fig.savefig("test.png")
        plot.show(block=True)
        file.close()


#Fomrat of simulation is input file in std format, MWh of battery storage, dirty charging boolean
#Dirty charging says that lfg should always be used to fill the battery, and used before taking energy out of the battery

# clean("Mecca_75MW.csv")
# wind_leap("Wind_Boulevard.csv")
# wind_leap("North_palm_wind.csv")

# data_source = "proj2_dataset.csv"
# os.remove("sim_out.csv")
# simulate(data_source, 1000, True)

# data_source = "full_sim.csv"
# try:
#     os.remove("sim_out_new.csv")
# except:
#     pass
# simulate_new(data_source, 500)

# data_source = "full_sim.csv"
# try:
#     os.remove("sim_out_new.csv")
# except:
#     pass
# simulate_base_ao(data_source, 1000)

# data_source = "full_sim.csv"
# try:
#     os.remove("sim_out_new.csv")
# except:
#     pass
# simulate_outage(data_source, 500, 210)

data_source = "sim_out_new.csv"
# data_source = "sim_s1w1b0b0.csv"
# data_source = "sim_s1w1b500b0.csv"
# data_source = "sim_s1w1b0b20.csv"
# data_source = "sim_s2w1b1000b10.csv"
# gen_daily_plots(data_source, 210, 2, "paper", 1)
# gen_daily_plots(data_source, 208 , 3, "view", 1)

# data_source = "sim_s2w2b500b22.csv"
# gen_daily_plots(data_source, 341, 3, "paper", 15/22) #batt day
# gen_daily_plots(data_source, 138, 3, "paper", 15/22) #spring
# gen_daily_plots(data_source, 208, 3, "paper", 15/22) #peak summer
# gen_daily_plots(data_source, 40, 3, "paper", 15/22) #winter
# gen_daily_plots(data_source, 313, 3, "paper", 15/22) #fall

gen_daily_plots(data_source, 210, 4, "paper", 15/22) #n-1



