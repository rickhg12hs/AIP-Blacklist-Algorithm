from inspect import getmembers, isfunction
from datetime import datetime
import shutil
import pandas as pd
from whitelist_module import *
import linear_models
from data_processing_functions import *
from rf_ml_models import *
from data_aggregation import *
import numpy as np

print('Starting main AIP script')

# Full path to directory where all the files will be stored
# (a)
AIP_output_data_directory = os.environ['output_folder']

startTime = datetime.now()

# Open the file that stored the selected modules, and store the selections in
# a list.
# file_for_functions = os.environ['output_folder'] + '/Selected_modules.csv'
#
# with open(file_for_functions, 'r') as file:
#     list_of_functions_that_were_choosen = []
#     for line in csv.reader(file):
#         if not line:
#             break
#         else:
#             list_of_functions_that_were_choosen.extend(line)
#
# functions_list = [o for o in getmembers(linear_models) if isfunction(o[1])]

current_directory = os.getcwd()

FP_log_file = AIP_output_data_directory + '/FP_log_file.csv'

# # Full path to the  folder where the program will look for new data files. It will look in the file and only process the
# # files it has not precessed yet. It will process every file it does not recognize.
# # (b)
folder_path_for_raw_Splunk_data = AIP_output_data_directory + '/Input_Data'
#
# # Full path to the file where the program will record the data files it processes
# # (c)
record_file_path_for_processed_Splunk_files = AIP_output_data_directory + '/Processed_Splunk_Files.txt'
#
# # A complete list of every IP seen by the program since it was started
# # (d)
# record_file_path_to_known_IPs = AIP_output_data_directory + '/Known_IPs.txt'
#
# # Full path to the file where the data flows for each IP are stored. Includes all the data the program has received
# # since it was started. This is NOT the file that contains the ratings.
# # (e)
# record_file_path_for_absolute_data = AIP_output_data_directory + '/Absolute_Data.csv'
#
# # Full path to folder that wil contain the daily rating files. This is a FOLDER!!
# # (f)
# directory_path_historical_ratings = AIP_output_data_directory + '/Historical_Ratings'
#
#
# # >>>>>>>>>>>>>>> Call the find new file function and define the time reference point for the aging function
new_data_files, date = find_new_data_files(folder_path_for_raw_Splunk_data, record_file_path_for_processed_Splunk_files,
                                           AIP_output_data_directory)
# print("New data files: ", new_data_files)
#
# with open(AIP_output_data_directory + "/log.txt", "a") as myfile:
#     myfile.write('There are ' + str(len(new_data_files)) + ' new data files to process' + "\n")
#     myfile.write('Files are ' + str(new_data_files) + "\n")
# current_time = datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 1).timestamp()
#
# with open(AIP_output_data_directory + "/log.txt", "a") as myfile:
#     myfile.write(str(startTime) + "\n")
#     myfile.write("AIP started" + "\n")
#
# # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Blacklist Files <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# # Path to the file that will contain top IPs from today's data only. Program will overwrite the previous days data.
# # (g)
# top_IPs_seen_today = directory_path_historical_ratings + '/Seen_today_Only/' + date + '_new_blacklist.csv'
#
# # Path to file that will contain the top IPs from the data from all time. Program will overwrite the previous days data.
# # (h)
# top_IPs_for_all_time = directory_path_historical_ratings + '/Prioritize_Consistent/' + date + '_pc_blacklist.csv'
#
# # Path to file that will have the ratings that will prioritize the IPs that are newer over older ones based on
# # all the data.
# top_IPs_all_time_newer_prioritized = directory_path_historical_ratings + '/Prioritize_New/' + date + '_pn_blacklist.csv'
#
# # Path to file that will save the traditional blacklist
# traditional_blacklist = directory_path_historical_ratings + '/Traditional/' + date + '_trad_blacklist.csv'
#
# # File that will be storing the run times for this script
time_file = AIP_output_data_directory + '/Times.csv'
#
# # Files for keeping track of aging modifiers
# path_aging_modifier_pc = AIP_output_data_directory + '/Aging-modifiers-pc.csv'
# path_aging_modifier_pn = AIP_output_data_directory + '/Aging-modifiers-pn.csv'
#
#
# # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Linear Models <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#
# print("Starting Linear models")
# # Load the and process the Data
#
# list_of_known_data_flows, list_of_known_IPs_in_data = open_sort_abs_file(record_file_path_for_absolute_data)
#
# list_of_new_data_flows, list_of_IPs_in_new_data = open_sort_new_file_linear(folder_path_for_raw_Splunk_data, new_data_files)
#
# unknown_IP_flows_from_new_data, unknown_IPs_from_new_data, known_IP_data_flows_from_new_data, known_IPs_from_new_data\
#     = sort_IPs_from_data(list_of_known_IPs_in_data, list_of_new_data_flows)
#
# write_unkown_IPs_to_data_file(unknown_IPs_from_new_data, record_file_path_to_known_IPs)
#
# update_records_files(record_file_path_for_absolute_data, known_IP_data_flows_from_new_data,
#                      unknown_IP_flows_from_new_data, current_time, current_directory, AIP_output_data_directory, FP_log_file)
#
# number_of_lines = len(open(record_file_path_for_absolute_data).readlines())
# with open(AIP_output_data_directory + "/log.txt", "a") as myfile:
#     myfile.write('Number of lines in absolute data' + str(number_of_lines) + "\n")
#
#
# # Pull the three functions that were choosen by the user from the dictionary of functions.
#
# PCF = getattr(linear_models, list_of_functions_that_were_choosen[0])
# PNF = getattr(linear_models, list_of_functions_that_were_choosen[1])
# OTF = getattr(linear_models, list_of_functions_that_were_choosen[2])
#
# # Call the create blacklist function for each of the three user input functions
# create_final_blacklist(top_IPs_for_all_time, get_updated_flows(record_file_path_for_absolute_data), PCF, AIP_output_data_directory,
#                        date, list_of_functions_that_were_choosen, current_time, path_aging_modifier_pc)
# create_final_blacklist(top_IPs_all_time_newer_prioritized, get_updated_flows(record_file_path_for_absolute_data), PNF,
#                        AIP_output_data_directory, date, list_of_functions_that_were_choosen, current_time, path_aging_modifier_pn)
# create_final_blacklist(top_IPs_seen_today, unknown_IP_flows_from_new_data, OTF, AIP_output_data_directory, date,
#                        list_of_functions_that_were_choosen, current_time, path_aging_modifier_pc)
#
#
# shutil.copy2(record_file_path_to_known_IPs, traditional_blacklist)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Random Forest Models <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

new_24_hour_data = AIP_output_data_directory + '/ML_Model_Data/new_24_hour_data.csv'
previous_24_hour_data = AIP_output_data_directory + '/ML_Model_Data/previous_24_hour_data.csv'
concatenated_data_labeled = AIP_output_data_directory + '/ML_Model_Data/concatenated_data_labeled.csv'
previous_24_hour_data_labeled = AIP_output_data_directory + '/ML_Model_Data/previous_24_hour_data_labeled.csv'
C_model_output_1_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_1_day/' + date + '_rf_concatenated_backlist_1_day.csv'
# C_model_output_2_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_2_day/' + date + '_rf_concatenated_backlist_2_day.csv'
# C_model_output_3_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_3_day/' + date + '_rf_concatenated_backlist_3_day.csv'
# C_model_output_4_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_4_day/' + date + '_rf_concatenated_backlist_4_day.csv'
# C_model_output_5_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_5_day/' + date + '_rf_concatenated_backlist_5_day.csv'
# C_model_output_6_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_6_day/' + date + '_rf_concatenated_backlist_6_day.csv'
# C_model_output_7_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_7_day/' + date + '_rf_concatenated_backlist_7_day.csv'
# C_model_output_8_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_8_day/' + date + '_rf_concatenated_backlist_8_day.csv'
# C_model_output_9_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_9_day/' + date + '_rf_concatenated_backlist_9_day.csv'
# C_model_output_10_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_10_day/' + date + '_rf_concatenated_backlist_10_day.csv'


A_model_ouptut = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Aggregated/' + date + '_rf_aggregate_backlist.csv'

if os.stat(previous_24_hour_data_labeled).st_size == 0:
    print('No label-able past data. Skipping ML models')
else:
    print("Starting random forest models")
    print("Concatenation Model")
    # --------- Concatenation Random Forest Model ----------
    # Process the training data
    if os.stat(concatenated_data_labeled).st_size == 0:
        print('No historical Data. Taking first option')
        c_data_new = load_data(previous_24_hour_data_labeled)
        c_data_new = add_row(c_data_new)
        y_all, X_all = separate_labels_data(c_data_new)
        X_train, X_test, y_train, y_test = bin_data(y_all, X_all)

        # Process the data we will be predicting on
        first_day_for_predictions = process_old_data(new_24_hour_data)

        first_day_for_ips = load_data(new_24_hour_data)
        ips = extract_ips_from_pandas_dataframe(first_day_for_ips)

        # Train a model and find good paramaters
        best_params = find_best_param(X_train, X_test, y_train, y_test)
        # with open(AIP_output_data_directory + "/paramaters.txt", "a") as myfile:
        #    myfile.write(best_params)

        # Train a model using best params, using the whole dataset this time
        predictions_1_day = train_on_complete_data(X_all, y_all, first_day_for_predictions, best_params)

        blacklist_C_1_day = create_blacklist(predictions_1_day, ips)

        write_blacklist_to_file(C_model_output_1_day, blacklist_C_1_day)

        c_data_new.to_csv(concatenated_data_labeled, index=False)
    else:
        print('There is historical data. Taking second option')
        path, dirs, files = next(os.walk(folder_path_for_raw_Splunk_data))
        days_in_historical_data = len(files)

        c_data_historical = load_data(concatenated_data_labeled)
        c_data_new = load_data(previous_24_hour_data_labeled)
        c_data_new = add_row(c_data_new)
        combined_data = combine_data_pandas(c_data_historical, c_data_new)
        if days_in_historical_data - 1 > 30:
            lines_to_drop = len(combined_data)//30
            combined_data.drop(pd.Series(np.arange(0, lines_to_drop, 1)))
            print("Dropped", lines_to_drop, ' lines')
        else:
            print("Days in Data: ", days_in_historical_data)

        y_all, X_all = separate_labels_data(combined_data)
        X_train, X_test, y_train, y_test = bin_data(y_all, X_all)

        # Find best params
        best_params = find_best_param(X_train, X_test, y_train, y_test)

        # Count how many days of data we have in combined data
        first_day_for_predictions = load_data(new_24_hour_data)
        combined_data_for_predicting = combine_data_pandas(combined_data.loc[:, ~combined_data.columns.isin(['Label'])],
                                                           first_day_for_predictions)
        if days_in_historical_data - 1 > 30:
            average_flows_per_day = len(combined_data_for_predicting) / 30
        else:
            average_flows_per_day = len(combined_data_for_predicting) / days_in_historical_data

        print('Number of total flows: ', len(combined_data_for_predicting))
        for x in range(1, 26, 3):
            if int(days_in_historical_data) >= x:
                print('Predicing on ', x, 'days of data')
                # Calculate number of data frames to extract
                number_of_data_frames = int(x * average_flows_per_day)
                print('Number of flows: ', number_of_data_frames)
                # Take the specified number from the end of the combined dataframe
                data_frame = return_rows_by_index(combined_data_for_predicting, -number_of_data_frames)
                # Create a subframe that does not contain the following rows
                data_no_label = data_frame.loc[:, ~data_frame.columns.isin(['AV_Events', 'SrcAddr'])]
                data_no_label = add_row(data_no_label)
                # Create a list of ips in the dataframe
                data_ips = data_frame['SrcAddr'].tolist()
                predictions = train_on_complete_data(X_all, y_all, data_no_label, best_params)
                blacklist = list(set(create_blacklist(predictions, data_ips)))
                file = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_' + str(x) + \
                         '_day/' + date + '_rf_concatenated_backlist_' + str(x) + '_day.csv'
                print('Writing to: ', file)
                write_blacklist_to_file(file, blacklist)

        # write_blacklist_to_file(C_model_output_1_day, list_of_blacklists[0])
        # print('Creating blacklist from 1 day of data')
        # if len(list_of_blacklists) >= 2:
        #     write_blacklist_to_file(C_model_output_2_day, list_of_blacklists[1])
        #     print('Creating blacklist from 2 days of data')
        # if len(list_of_blacklists) >= 3:
        #     write_blacklist_to_file(C_model_output_3_day, list_of_blacklists[2])
        #     print('Creating blacklist from 3 days of data')
        # if len(list_of_blacklists) >= 4:
        #     write_blacklist_to_file(C_model_output_4_day, list_of_blacklists[3])
        #     print('Creating blacklist from 4 days of data')
        # if len(list_of_blacklists) >= 5:
        #     write_blacklist_to_file(C_model_output_5_day, list_of_blacklists[4])
        #     print('Creating blacklist from 5 days of data')
        # if len(list_of_blacklists) >= 6:
        #     write_blacklist_to_file(C_model_output_6_day, list_of_blacklists[5])
        #     print('Creating blacklist from 6 days of data')
        # if len(list_of_blacklists) >= 7:
        #     write_blacklist_to_file(C_model_output_7_day, list_of_blacklists[6])
        #     print('Creating blacklist from 7 days of data')
        # if len(list_of_blacklists) >= 8:
        #     write_blacklist_to_file(C_model_output_8_day, list_of_blacklists[7])
        #     print('Creating blacklist from 8 days of data')
        # if len(list_of_blacklists) >= 9:
        #     write_blacklist_to_file(C_model_output_9_day, list_of_blacklists[8])
        #     print('Creating blacklist from 9 days of data')
        # if len(list_of_blacklists) >= 10:
        #     write_blacklist_to_file(C_model_output_10_day, list_of_blacklists[9])
        #     print('Creating blacklist from 10 days of data')


        # Process the data we will be predicting on
        # first_day_for_predictions = process_old_data(new_24_hour_data)
        # second_day_for_predictions = process_old_data(previous_24_hour_data)
        # two_day_combined_data = combine_data_pandas(first_day_for_predictions, second_day_for_predictions)
        #
        # first_day_for_ips = load_data(new_24_hour_data)
        # second_day_for_ips = load_data(previous_24_hour_data)
        # two_day_combined_data_ips = combine_data_pandas(first_day_for_ips, second_day_for_ips)
        # one_day_ips = extract_ips_from_pandas_dataframe(first_day_for_ips)
        # two_day_ips = extract_ips_from_pandas_dataframe(two_day_combined_data_ips)


        # Train a model using best params, using the whole dataset this time
        # predictions_1_day = train_on_complete_data(X_all, y_all, first_day_for_predictions, best_params)
        # predictions_2_day = train_on_complete_data(X_all, y_all, two_day_combined_data, best_params)
        #
        # blacklist_C_1_day = create_blacklist(predictions_1_day, one_day_ips)
        # blacklist_C_2_day = create_blacklist(predictions_2_day, two_day_ips)

        # write_blacklist_to_file(C_model_output_1_day, blacklist_C_1_day)
        # write_blacklist_to_file(C_model_output_2_day, blacklist_C_2_day)

        combined_data.to_csv(concatenated_data_labeled, index=False)

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
