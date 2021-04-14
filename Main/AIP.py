from inspect import getmembers, isfunction
from datetime import datetime
import shutil
from whitelist_module import *
import linear_models
from data_processing_functions import *
from rf_ml_models import *
from data_aggregation import *

print('Starting main AIP script')

# Full path to directory where all the files will be stored
# (a)
AIP_output_data_directory = os.environ['output_folder']

startTime = datetime.now()

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

functions_list = [o for o in getmembers(linear_models) if isfunction(o[1])]

current_directory = os.getcwd()

FP_log_file = AIP_output_data_directory + '/FP_log_file.csv'

# Full path to the  folder where the program will look for new data files. It will look in the file and only process the
# files it has not precessed yet. It will process every file it does not recognize.
# (b)
folder_path_for_raw_Splunk_data = AIP_output_data_directory + '/Input_Data'

# Full path to the file where the program will record the data files it processes
# (c)
record_file_path_for_processed_Splunk_files = AIP_output_data_directory + '/Processed_Splunk_Files.txt'

# A complete list of every IP seen by the program since it was started
# (d)
record_file_path_to_known_IPs = AIP_output_data_directory + '/Known_IPs.txt'

# Full path to the file where the data flows for each IP are stored. Includes all the data the program has received
# since it was started. This is NOT the file that contains the ratings.
# (e)
record_file_path_for_absolute_data = AIP_output_data_directory + '/Absolute_Data.csv'

# Full path to folder that wil contain the daily rating files. This is a FOLDER!!
# (f)
directory_path_historical_ratings = AIP_output_data_directory + '/Historical_Ratings'


# >>>>>>>>>>>>>>> Call the find new file function and define the time reference point for the aging function
new_data_files, date = find_new_data_files(folder_path_for_raw_Splunk_data, record_file_path_for_processed_Splunk_files,
                                           AIP_output_data_directory)
print("New data files: ", new_data_files)

with open(AIP_output_data_directory + "/log.txt", "a") as myfile:
    myfile.write('There are ' + str(len(new_data_files)) + ' new data files to process' + "\n")
    myfile.write('Files are ' + str(new_data_files) + "\n")
current_time = datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 1).timestamp()

with open(AIP_output_data_directory + "/log.txt", "a") as myfile:
    myfile.write(str(startTime) + "\n")
    myfile.write("AIP started" + "\n")

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
time_file = AIP_output_data_directory + '/Times.csv'

# Files for keeping track of aging modifiers
path_aging_modifier_pc = AIP_output_data_directory + '/Aging-modifiers-pc.csv'
path_aging_modifier_pn = AIP_output_data_directory + '/Aging-modifiers-pn.csv'


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Linear Models <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

print("Starting Linear models")
# Load the and process the Data

list_of_known_data_flows, list_of_known_IPs_in_data = open_sort_abs_file(record_file_path_for_absolute_data)

list_of_new_data_flows, list_of_IPs_in_new_data = open_sort_new_file_linear(folder_path_for_raw_Splunk_data, new_data_files)

unknown_IP_flows_from_new_data, unknown_IPs_from_new_data, known_IP_data_flows_from_new_data, known_IPs_from_new_data\
    = sort_IPs_from_data(list_of_known_IPs_in_data, list_of_new_data_flows)

write_unkown_IPs_to_data_file(unknown_IPs_from_new_data, record_file_path_to_known_IPs)

update_records_files(record_file_path_for_absolute_data, known_IP_data_flows_from_new_data,
                     unknown_IP_flows_from_new_data, current_time, current_directory, AIP_output_data_directory, FP_log_file)

number_of_lines = len(open(record_file_path_for_absolute_data).readlines())
with open(AIP_output_data_directory + "/log.txt", "a") as myfile:
    myfile.write('Number of lines in absolute data' + str(number_of_lines) + "\n")


# Pull the three functions that were choosen by the user from the dictionary of functions.

PCF = getattr(linear_models, list_of_functions_that_were_choosen[0])
PNF = getattr(linear_models, list_of_functions_that_were_choosen[1])
OTF = getattr(linear_models, list_of_functions_that_were_choosen[2])

# Call the create blacklist function for each of the three user input functions
create_final_blacklist(top_IPs_for_all_time, get_updated_flows(record_file_path_for_absolute_data), PCF, AIP_output_data_directory,
                       date, list_of_functions_that_were_choosen, current_time, path_aging_modifier_pc)
create_final_blacklist(top_IPs_all_time_newer_prioritized, get_updated_flows(record_file_path_for_absolute_data), PNF,
                       AIP_output_data_directory, date, list_of_functions_that_were_choosen, current_time, path_aging_modifier_pn)
create_final_blacklist(top_IPs_seen_today, unknown_IP_flows_from_new_data, OTF, AIP_output_data_directory, date,
                       list_of_functions_that_were_choosen, current_time, path_aging_modifier_pc)


shutil.copy2(record_file_path_to_known_IPs, traditional_blacklist)

with open(AIP_output_data_directory + "/log.txt", "a") as myfile:
    myfile.write('Total Runtime' + str(datetime.now() - startTime) + "\n")
    myfile.write('---------------- AIP run complete ----------------' + "\n")

# Append the time that it took to a file
with open(time_file, 'a') as new_file_another:
        wr2 = csv.writer(new_file_another, quoting=csv.QUOTE_ALL)
        list4 = []
        list4.append(date)
        list4.append(datetime.now() - startTime)
        wr2.writerow(list4)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Random Forest Models <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

new_24_hour_data = AIP_output_data_directory + '/ML_Model_Data/new_24_hour_data.csv'
aggregate_data = AIP_output_data_directory + '/ML_Model_Data/aggregate_data.csv'
aggregate_data_labeled = AIP_output_data_directory + '/ML_Model_Data/aggregate_data_labeled.csv'
concatinated_data_labeled = AIP_output_data_directory + '/ML_Model_Data/concatinated_data_labeled.csv'
C_model_output = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatinated/' + date + '_rf_concatinated_backlist.csv'
A_model_ouptut = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Aggregated/' + date + '_rf_aggregate_backlist.csv'

if os.stat(aggregate_data_labeled).st_size == 0:
    print('No label-able past data. Skipping ML models')
else:
    print("Starting random forest models")

    # --------- Concatination Random Forest Model ----------
    # Process the training data
    c_data = load_data(concatinated_data_labeled)
    c_data = add_row(c_data)
    y_all, X_all = separate_labels_data(c_data)
    X_train, X_test, y_train, y_test = bin_data(y_all, X_all)

    # Process the data we will be predicting on
    processed_data = process_old_data(new_24_hour_data)
    list_of_new_data_flows, ips_in_data_C = open_sort_new_file(new_24_hour_data)

    # Train a model and find good paramaters
    best_params = find_best_param(X_train, X_test, y_train, y_test)

    # Train a model using best params, using the whole dataset this time
    predictions = train_on_complete_data(X_all, y_all, processed_data, best_params)

    blacklist_C = create_blacklist(predictions, list_of_new_data_flows)

    write_blacklist_to_file(C_model_output, blacklist_C)

    # --------- Aggregation Random Forest Model ----------
    # Process the training data
    a_data = load_data(aggregate_data_labeled)
    a_data = add_row(a_data)
    y_all, X_all = separate_labels_data(a_data)
    X_train, X_test, y_train, y_test = bin_data(y_all, X_all)

    # Process the data we will be predicting on
    processed_data = process_old_data(aggregate_data)
    list_of_new_data_flows, ips_in_data_A = open_sort_new_file(aggregate_data)

    # Train a model and find good paramaters
    best_params = find_best_param(X_train, X_test, y_train, y_test)

    # Train a model using best params, using the whole dataset this time
    predictions = train_on_complete_data(X_all, y_all, processed_data, best_params)

    blacklist_A = create_blacklist(predictions, list_of_new_data_flows)

    write_blacklist_to_file(A_model_ouptut, blacklist_A)
