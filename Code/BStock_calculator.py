# Building stock turnover calculator
# IESVic - 2023

# This tool calculates the comercial and residential building stock turnover based on equations and data from Tamara Knittel's work and research.
# Code by: Cristiano Curi Fernandes - Co-op research assistant at IESVic (2023)


# Import relevant modules
import numpy as np
import os
import pandas as pd
import math


#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/

# Residential Stock

# Inputs: 
# Dem. rate
# New /retro construction
# EUI

# Output:
# Floor space [A] (total) = Av + Anew - Ademo = Eq12 + Eq14 - Eq15
# The total floor space A(y) of today’s building stock as the sum of area per vintage
# SH = 
# WH

# Results should be presented for last year of time series (ex: 2018)

#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/

# Get data file

stock_file = "./Documents and References\Stock_Formatted_Data_File.xlsx"
stock_data = pd.DataFrame(pd.read_excel(stock_file, sheet_name="Input"))
#print(stock_data.head())

# Global variables
included, Year, Demo_b, New_b, Retro_b, EUI, PG = stock_data.T.values
EUI_history = [0.52499874,	0.465893215,	0.391118354,	0.318520436,	0.258358114,	0.208521154,	
       0.206230547,	0.176287146,	0.164598772,	0.150696297,	0.067, 0.054, 0.054]



#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/#/


# Create vintages as a class

class Vintage:
    # Class to create a vintage period for building stock
    # A vintage period is a short time series which captures the total, 
    # new construction, demolished, and retrofitted floor space for a number of years
    
    def __init__(self, s_year, starting_building_stock=295.745, remaining_start_stock=281) -> None:
        # Class initializer (all class attributes are declared here)
        # The initial building stock given by default is from 2016
        
        self.__vintage_history = pd.DataFrame(columns=['Years', 'New', 'Demolished', 'Retrofitted', 'Total', 'Average EUI']) # Dictionary with all vintages created
        self.__vintage = [] # Years in vintage period
        self.__demo_FS = [] # Demolished floor space in vintage periiod
        self.__retro_FS = [] # Retrofitted floor space in vintage period
        self.__new_FS = [] # New construction (floor space) in vintage period
        self.__total_FS = [] # Total floor space in vintage period
        self.__historical_FS = [8.369309574, 10.53901598, 37.9964877, 35.23895826, 59.0961685, 23.70776522,
                                	24.33461767, 30.60991933, 25.99295, 16.90715]

        self.__space_HD = [] # Space heat demand for vintage period
        self.__water_HD = [] # Water heat demand for vintage period

        self.__start_year = s_year # First year of vintage period
        self.__starting_stock = starting_building_stock
        self.__remaining_stock = remaining_start_stock


        self.__population = 4859250 # Initial population to the model
        self.__reference_FS = 10.85 * self.__population  # Reference floor space (from 1946-1960)
        self.__total_area = 58.7 # Total floor space at start
        self.__SH_start = 71.53  # Space heat demand at start

    def reset_vintage(self, new_start, new_stock):
        # Method for resetting the vintage periods
        self.__init__(new_start, new_stock)

    def add_to_vintage(self,vin_end):
        # This method adds years to the vintage period until vintage end (vin_end)
        curr_year = self.__start_year

        while curr_year <= vin_end:
            self.__vintage.append(curr_year)
            curr_year += 1
        
    
    def add_FS(self): #, fs, type = "new"):
        y = self.__start_year # Placeholder year
        current_stock, remaining_stock_start, current_pos = self.__starting_stock, self.__remaining_stock, 0
        Anew, Aretro, Ademo = current_stock, 0, current_stock # Starting values for new, retrofitted, and demolished construction
        

        while y <= self.__vintage[-1]: # Get last year of vintage period
            self.__total_FS.append(current_stock)
            '''
            if y is self.__start_year:
                nc_rate, retro_rate, demo_rate = 0, 0, 0
            else:
                nc_rate, retro_rate, demo_rate = New_b[current_pos], Retro_b[current_pos], Demo_b[current_pos]
            '''
            nc_rate, retro_rate, demo_rate = New_b[current_pos], Retro_b[current_pos], Demo_b[current_pos]



            Anew = abs(current_stock/100 * nc_rate)
            self.__new_FS.append(Anew)

            Ademo = abs(current_stock/100 * demo_rate)
            self.__demo_FS.append(Ademo)

            remaining_stock_start = remaining_stock_start - Ademo 

            Aretro = abs(remaining_stock_start/100 * retro_rate)
            self.__retro_FS.append(Aretro)


            current_stock = round(current_stock + Anew - Ademo, 2)
            y += 1 # Go to next year
            self.__population = self.__population * PG[current_pos] # Update population for next year
            current_pos += 1 # update position for data frames

    def change_vintage_period(self, new_y, new_end_y):
        # This method creates a new vintage from scratch with the new start and end years given to it
        
        EUI_current = sum(self.__total_FS * EUI[:(self.__vintage[-1] - self.__start_year)+1]) / sum(self.__total_FS)

        self.__vintage_history.loc['Vintage ' + str(self.__vintage[0]) + 
        ' - ' + str(self.__vintage[-1])] = [self.__vintage, self.__new_FS, self.__demo_FS, self.__retro_FS, self.__total_FS, EUI_current]
        
        #print(self.__vintage_history["Total"].iloc[-1][-1])
        self.reset_vintage(new_start=new_y, new_stock=self.__vintage_history["Total"].iloc[-1][-1]) # Create new vintage using the last vintage's last building stock as starting stock
        self.add_to_vintage(new_end_y)
        self.add_FS()

        '''
        # Proof-reading vintage history
        if self.__vintage_history["New"] == [] or self.__vintage_history["Retrofitted"] == [] or self.__vintage_history["Demolished"] == [] or self.__vintage_history["Total"] == []:
            print("No previous vintage on record, please start by creating your virst vintage with the .add_to_vintage() method and add the floor space to it with the .add_FS() method")
            self.__vintage_history = {}
        '''

    def check_vintage(self, type="total", current=True):
        # Method for displaying current building stock for each vintage type
        print("Measurements are given in squared meters \n")
        if current == True:
            if type is "total":
                print("\nTotal floor space per year in vintage ", self.__vintage[0], " - ", self.__vintage[-1],
                    "is: ", self.__total_FS)
            elif type is "new":
                print("\nTotal new floor space per year in vintage ", self.__vintage[0], " - ", self.__vintage[-1],
                    "is: ", self.__new_FS)
            elif type is "retrofit":
                print("\nTotal retrofitted floor space per year in vintage ", self.__vintage[0], " - ", self.__vintage[-1],
                    "is: ", self.__retro_FS)
            else:
                print("Unrecognized type of floor space. Did you mean 'new', 'retrofit', or 'total' instead?")
        else:
            print(self.__vintage_history)
    
    def get_avg_EUI(self, vintage_type="total"): # Debugging values not quite right (need clarification on the meaning of the term "vintage")
        #EUI_avg = sum(self.__new_FS * EUI[:(self.__vintage[-1] - self.__start_year)+1]) / self.__total_FS[-1] 
        #+ sum(self.__retro_FS * EUI[:(self.__vintage[-1] - self.__start_year)+1]) / self.__total_FS[-1] 
        #+ sum(self.__demo_FS * EUI[:(self.__vintage[-1] - self.__start_year)+1]) / self.__total_FS[-1] #/ (sum(self.__total_FS)) # Average EUI        
        
        print(EUI)
        current_fs = [272.79, 275.81, 278.98, 282.2]
        #for i,j,k in zip(self.__total_FS, self.__demo_FS, self.__retro_FS):
        #   current_fs.append(i - j - k)
        
        EUI_avg = []
        for total_fs, curr_fs, curr_eui in zip(self.__total_FS, self.__historical_FS, EUI_history):
            eui =  0.171 * sum(self.__new_FS)  + sum(self.__retro_FS) * 0.171 + (curr_fs*curr_eui)
            EUI_avg.append(eui / total_fs)
                        


        #EUI_avg = (0.171 * sum(self.__new_FS) 
        #+ sum(self.__retro_FS) * 0.171 + sum(eui_multiplier)) / sum(self.__total_FS)

        print("-"*10)

        print("New ", self.__new_FS)
        print("Demo ", self.__demo_FS)
        print("Retro ", self.__retro_FS)
        print("Total ", self.__total_FS)
        print("EUI ", EUI_history)
        print("\nThe average EUI for total floor space in the period between ", self.__start_year, " and ", self.__vintage[-1], " is: ", EUI_avg)
        print("-"*10)


        


my_vintage = Vintage(2017)
my_vintage.add_to_vintage(2020)


my_vintage.add_FS()
my_vintage.get_avg_EUI()
my_vintage.check_vintage("total")


print("-" * 8)
'''
my_vintage.change_vintage_period(2020,2025)
#my_vintage.get_avg_EUI()
my_vintage.check_vintage("total", False)
'''