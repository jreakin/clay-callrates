# Use this with the "TRENDING WITH VIEWS" report I made.
# If you don't have access to that, any "Handled and Abandoned Trending" report with the  "Contact Service Queue Activity by Interval" view works as well.

import csv
import openpyxl
import easygui
from typing import Generator
import os # used to delete temp file

start_times: list[str] = [] # A list of the actual start time intervals in each day. 8 am, 9 am, etc.
end_times: list[str] = [] # Like above, but the end time. Each interval is one hour, ie 8 AM - 9 AM.

'''
The reports we feed into this script leave a blank row on top and some extra data on the bottom.
We stop parsing when it hits a second blank cell, meaning we need to keep track of if we already skipped the first one.
'''
first_row_skipped = False 

interval_dict: dict[str: dict[str : int]] = {} # Dictionary is structured like {1-1-1901 : {8:00:00 AM: 300, 9:00:00 AM : 500, ...}, 1-2-1901 : ...}
input_rows: list[list[str] | tuple[str]] = [] # Rows to write to the temp file. csv returns lists, openpyxl returns tuples.
input_spreadsheet: str = easygui.fileopenbox(msg = 'Select the input file (can be csv or xlsx). Only the first sheet of Excel files will be read. Output by default is "output.csv', 
                                     default='*', 
                                     multiple=False,
                                     filetypes = ['*.csv', '*.xlsx'])

if not input_spreadsheet:
    print('No input file selected.')
    exit()

if input_spreadsheet[-3:] == 'csv':    
    with open(input_spreadsheet, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)        
        for row in reader:
            if row[0] == None:
                if not first_row_skipped:
                    first_row_skipped = True
                else:
                    break
                continue
            else:
                input_rows.append(row)
            
if input_spreadsheet[-4:] == 'xlsx':
    workbook = openpyxl.load_workbook(input_spreadsheet)
    sheet = workbook.worksheets[0]
    for row in sheet.iter_rows(values_only=True):
        if row[0] == None:
            if not first_row_skipped:
                first_row_skipped = True
                continue
            else:
                break            
        else:
            input_rows.append(row)

with open('temp_file.csv', 'w', newline='') as temp:
    writer = csv.writer(temp)
    for row in input_rows:
        writer.writerow(row)
input_file = 'temp_file.csv'

def row_generator() -> Generator:     
    with open(input_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                yield row
            except Exception as e:
                print("Invalid row.\n", e)

row_gen = row_generator()

for row in row_gen:
    split_interval_start = row['Interval Start Time'].split()
    split_interval_end = row['Interval End Time'].split()
    int_start_time = " ".join(split_interval_start[-2:])
    int_end_time = " ".join(split_interval_end[-2:])
    day = split_interval_start[0]
    if int_start_time not in start_times:
        start_times.append(int_start_time)
    if int_end_time not in end_times:
        end_times.append(int_end_time)
    if day not in interval_dict.keys():
        interval_dict[day] = {int_start_time : 0}
    elif int_start_time not in interval_dict[day]:
        interval_dict[day][int_start_time] = 0
    try:
        interval_dict[day][int_start_time] += int(float(row['Calls Presented'])) # openpyxl treats cells a little different than the csv module, hence explicitly floating.
    except Exception as e:
        print(e)

days = list(interval_dict.keys())

output_csv = easygui.filesavebox("Select location to save output csv.", 
                    title="Save Location", 
                    default="output.csv", 
                    filetypes=["*.csv"] )

with open(output_csv, 'w', newline="") as output:
    writer = csv.writer(output)
    header = ["Interval Start Time", "Interval End Time"]
    for day in days:
        header.append(day)
    writer.writerow(header)
    for i in range(len(start_times)):
        row_numbers = []
        for day in days:
            try:
                row_numbers.append(interval_dict[day][start_times[i]])
            except KeyError as e:
                row_numbers.append(0) # catches if that particular day did not have this time interval. 
                print("Key error: day did not have this particular interval start time: \n", e)
        row_to_write = [start_times[i], end_times[i]]
        for item in row_numbers:
            row_to_write.append(item)
        writer.writerow(row_to_write)
try:
    os.remove('temp_file.csv')    
    print("Temp file removed successfully.")
except Exception as e:
    print("Unable to remove temp file automatically.\n", e)