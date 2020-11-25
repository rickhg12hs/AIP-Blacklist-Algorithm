from inspect import getmembers, isfunction
from netaddr import IPAddress, IPNetwork
import csv
import operator
from datetime import datetime
import shutil
import os
from Modules.whitelist_module import *
import Modules.main_modulev3
from Modules.update_historical_data import *

startTime = datetime.now()

print('AIP started')

# Open the file that stored the selected modules, and store the selections in
# a list.
file_for_functions = os.environ['output_folder'] + '/Selected_modules.csv'
with open(file_for_functions, 'r') as file:
    list_of_functions_that_were_choosen = []
    for line in csv.reader(file):
        if not line:
            break
        else:
            list_of_functions_that_were_choosen.extend(line)

# Generate a list of available fully defined sorting functions
functions_list = [o for o in getmembers(Modules.main_modulev3) if isfunction(o[1])]

# Full path to directory where all the files will be stored
# (a)
AIPP_direcory = os.environ['output_folder']

# Full path to the  folder where the program will look for new data files. It will look in the file and only process the
# files it has not precessed yet. It will process every file it does not recognize.
# (b)
folder_path_for_raw_Splunk_data = AIPP_direcory + '/Input_Data'

# Full path to the file where the program will record the data files it processes
# (c)
record_file_path_for_processed_Splunk_files = AIPP_direcory + '/Processed_Splunk_Files.txt'

# A complete list of every IP seen by the program since it was started
# (d)
record_file_path_to_known_IPs = AIPP_direcory + '/Known_IPs.txt'

# Full path to the file where the data flows for each IP are stored. Includes all the data the program has received
# since it was started. This is NOT the file that contains the ratings.
# (e)
record_file_path_for_absolute_data = AIPP_direcory + '/Absolute_Data.csv'

# Full path to folder that wil contain the daily rating files. This is a FOLDER!!
# (f)
directory_path_historical_ratings = AIPP_direcory + '/Historical_Ratings'


# >>>>>>>>>>>>>>> Call the find new file function and define the time reference point for the aging function
new_data_files, date = find_new_data_files(folder_path_for_raw_Splunk_data, record_file_path_for_processed_Splunk_files)
print('There are ', len(new_data_files), ' new data files to process')
current_time = datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 1).timestamp()

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Blacklist Files <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Path to the file that will contain top IPs from today's data only. Program will overwrite the previous days data.
# (g)
top_IPs_seen_today = directory_path_historical_ratings + '/Seen_today_Only/' + date + '_new_blacklist.csv'

# Path to file that will contain the top IPs from the data from all time. Program will overwrite the previous days data.
# (h)
top_IPs_for_all_time = directory_path_historical_ratings + '/Prioritize_Consistent/' + date + '_pc_blacklist.csv'

# Path to file that will have the ratings that will prioritize the IPs that are newer over older ones based on
# all the data.
top_IPs_all_time_newer_prioritized = directory_path_historical_ratings + '/Prioritize_New/' + date + '_pn_blacklist.csv'

# Path to file that will save the traditional blacklist
traditional_blacklist = directory_path_historical_ratings + '/Traditional/' + date + '_trad_blacklist.csv'

# File that will be storing the run times for this script
time_file = AIPP_direcory + '/Times.csv'

# Files for keeping track of aging modifiers
path_aging_modifier_pc = AIPP_direcory + '/Aging-modifiers-pc.csv'
path_aging_modifier_pn = AIPP_direcory + '/Aging-modifiers-pn.csv'


def sort_data_decending(data):
    list_as_dictionary = {}
    for entry in data:
        list_as_dictionary[entry[0]] = entry[1]
    return sorted(list_as_dictionary.items(), key=operator.itemgetter(1), reverse=True)


# Now call all the functions on the data

list_of_known_data_flows, list_of_known_IPs_in_data = open_sort_abs_file(record_file_path_for_absolute_data)

list_of_new_data_flows, list_of_IPs_in_new_data = open_sort_new_file(folder_path_for_raw_Splunk_data, new_data_files)

unknown_IP_flows_from_new_data, unknown_IPs_from_new_data, known_IP_data_flows_from_new_data, known_IPs_from_new_data\
    = sort_IPs_from_data(list_of_known_IPs_in_data, list_of_new_data_flows)

write_unkown_IPs_to_data_file(unknown_IPs_from_new_data, record_file_path_to_known_IPs)

update_records_files(record_file_path_for_absolute_data, known_IP_data_flows_from_new_data, unknown_IP_flows_from_new_data)


number_of_lines = len(open(record_file_path_for_absolute_data).readlines())
print(number_of_lines)

def create_final_blacklist(path_to_file, data_from_absolute_file, function_to_use):
    with open(path_to_file, 'w') as new_file2:
        write2 = csv.writer(new_file2, quoting=csv.QUOTE_ALL)
        write2.writerow(('# Top IPs from data gathered in last 24 hours only', date))
        write2.writerow(('Number', 'IP address', 'Rating'))
        if function_to_use == getattr(Modules.main_modulev3, list_of_functions_that_were_choosen[1]):
            print('using pn')
            for x2, interesting_rating2 in enumerate(sort_data_decending(function_to_use(data_from_absolute_file, current_time, path_aging_modifier_pn))):
                if float(interesting_rating2[1]) >= 0.00008:
                    new_list2 = []
                    new_list2.append(x2)
                    new_list2.append(list(interesting_rating2)[0])
                    new_list2.append(interesting_rating2[1])
                    write2.writerow(new_list2)
                else:
                    break
        elif function_to_use == getattr(Modules.main_modulev3, list_of_functions_that_were_choosen[0]):
            print('using pc')
            for x2, interesting_rating2 in enumerate(sort_data_decending(function_to_use(data_from_absolute_file, current_time, path_aging_modifier_pc))):
                if float(interesting_rating2[1]) >= 0.0004:
                    new_list2 = []
                    new_list2.append(x2)
                    new_list2.append(list(interesting_rating2)[0])
                    new_list2.append(interesting_rating2[1])
                    write2.writerow(new_list2)
                else:
                    break
        else:
            print('using to')
            for x2, interesting_rating2 in enumerate(sort_data_decending(function_to_use(data_from_absolute_file, current_time, path_aging_modifier_pc))):
                new_list2 = []
                new_list2.append(x2)
                new_list2.append(list(interesting_rating2)[0])
                new_list2.append(interesting_rating2[1])
                write2.writerow(new_list2)



# Pull the three functions that were choosen by the user from the dictionary of functions.
# print(list_of_functions_that_were_choosen)

PCF = getattr(Modules.main_modulev3, list_of_functions_that_were_choosen[0])
PNF = getattr(Modules.main_modulev3, list_of_functions_that_were_choosen[1])
OTF = getattr(Modules.main_modulev3, list_of_functions_that_were_choosen[2])

# Call the create blacklist function for each of the three user input functions
create_final_blacklist(top_IPs_for_all_time, get_updated_flows(record_file_path_for_absolute_data), PCF)
create_final_blacklist(top_IPs_all_time_newer_prioritized, get_updated_flows(record_file_path_for_absolute_data), PNF)
create_final_blacklist(top_IPs_seen_today, unknown_IP_flows_from_new_data, OTF)


shutil.copy2(record_file_path_to_known_IPs, traditional_blacklist)

# Append the time that it took to a file
with open(time_file, 'a') as new_file_another:
        wr2 = csv.writer(new_file_another, quoting=csv.QUOTE_ALL)
        list4 = []
        list4.append(date)
        list4.append(datetime.now() - startTime)
        wr2.writerow(list4)
