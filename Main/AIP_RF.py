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

# # >>>>>>>>>>>>>>> Call the find new file function and define the time reference point for the aging function
new_data_files, date = find_new_data_files(folder_path_for_raw_Splunk_data, record_file_path_for_processed_Splunk_files,
                                           AIP_output_data_directory)

time_file = AIP_output_data_directory + '/Times.csv'


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Random Forest Models <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

new_24_hour_data = AIP_output_data_directory + '/ML_Model_Data/new_24_hour_data.csv'
previous_24_hour_data = AIP_output_data_directory + '/ML_Model_Data/previous_24_hour_data.csv'
concatenated_data_labeled = AIP_output_data_directory + '/ML_Model_Data/concatenated_data_labeled.csv'
previous_24_hour_data_labeled = AIP_output_data_directory + '/ML_Model_Data/previous_24_hour_data_labeled.csv'
C_model_output_1_day = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_1_day/' + date + '_rf_concatenated_backlist_1_day.csv'


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

        first_day_for_predictions = process_old_data(new_24_hour_data)

        first_day_for_ips = load_data(new_24_hour_data)
        ips = extract_ips_from_pandas_dataframe(first_day_for_ips)

        predictions_1_day = train_on_complete_data(X_all, y_all, first_day_for_predictions)

        blacklist_C_1_day = create_blacklist(predictions_1_day, ips)

        write_blacklist_to_file(C_model_output_1_day, blacklist_C_1_day, current_directory, AIP_output_data_directory)

        c_data_new.to_csv(concatenated_data_labeled, index=False)
    else:
        print('There is historical data. Taking second option')
        path, dirs, files = next(os.walk(folder_path_for_raw_Splunk_data))
        days_in_historical_data = len(files)

        c_data_historical = load_data(concatenated_data_labeled)
        c_data_new = load_data(previous_24_hour_data_labeled)
        c_data_new = add_row(c_data_new)
        all_data = combine_data_pandas(c_data_historical, c_data_new)

        y_all, X_all = separate_labels_data(all_data)
        X_train, X_test, y_train, y_test = bin_data(y_all, X_all)

        # Find best params
        # best_params = find_best_param(X_train, X_test, y_train, y_test)

        # Count how many days of data we have in combined data
        first_day_for_predictions = load_data(new_24_hour_data)
        combined_data_for_predicting = combine_data_pandas(all_data.loc[:, ~all_data.columns.isin(['Label'])],
                                                           first_day_for_predictions)
        if days_in_historical_data - 1 > 30:
            average_flows_per_day = len(combined_data_for_predicting) / 30
        else:
            average_flows_per_day = len(combined_data_for_predicting) / days_in_historical_data

        print('Number of total flows: ', len(combined_data_for_predicting))
        for x in range(1, 26, 3):
            if int(days_in_historical_data) >= x:
                print('Predicting on ', x, ' days of data')
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
                predictions = train_on_complete_data(X_all, y_all, data_no_label)
                blacklist = list(set(create_blacklist(predictions, data_ips)))
                file = AIP_output_data_directory + '/Historical_Ratings/Random_Forest_Concatenated_' + str(x) + \
                         '_day/' + date + '_rf_concatenated_backlist_' + str(x) + '_day.csv'
                print('Writing to: ', file)
                write_blacklist_to_file(file, blacklist, current_directory, AIP_output_data_directory)

        all_data.to_csv(concatenated_data_labeled, index=False)

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
