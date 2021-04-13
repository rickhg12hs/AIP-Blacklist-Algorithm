from inspect import getmembers, isfunction
from datetime import datetime
import shutil
from whitelist_module import *
import linear_models
from process_data import *
from rf_ml_model import *

# Full path to directory where all the files will be stored
# (a)
AIPP_direcory = os.environ['output_folder']

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


# >>>>>>>>> Needs to be here so it can be called immediately, fine what data
# files have not been processed.
def find_new_data_files(b, c):
    list_of_new_data_files = []
    list_of_data_files = os.listdir(b)
    dictionary_of_dates_on_files = {}
    with open(c, 'r') as record:
        list_of_processed_data_files = record.read().split('\n')
    for file in list_of_data_files:
        if file not in list_of_processed_data_files:
            list_of_new_data_files.extend([file])
            dictionary_of_dates_on_files[file[0:10]] = file
    for file12 in list_of_new_data_files:
        with open(c, 'a') as records_file1:
            records_file1.write(file12 + '\n')
    sorted_dates = sorted(dictionary_of_dates_on_files, key=lambda date: datetime.strptime(date, '%Y-%m-%d'))
    sorted_dates.reverse()
    with open(AIPP_direcory + "log.txt", "a") as myfile:
        myfile.write(str(sorted_dates) + "\n")
    return list_of_new_data_files, sorted_dates[0]

current_directory = os.getcwd()

FP_log_file = AIPP_direcory + '/FP_log_file.csv'

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
with open(AIPP_direcory + "/log.txt", "a") as myfile:
    myfile.write('There are ' + str(len(new_data_files)) + ' new data files to process' + "\n")
    myfile.write('Files are ' + str(new_data_files) + "\n")
current_time = datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 1).timestamp()

with open(AIPP_direcory + "/log.txt", "a") as myfile:
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
time_file = AIPP_direcory + '/Times.csv'

# Files for keeping track of aging modifiers
path_aging_modifier_pc = AIPP_direcory + '/Aging-modifiers-pc.csv'
path_aging_modifier_pn = AIPP_direcory + '/Aging-modifiers-pn.csv'


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Linear Models <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def update_records_files(e, list_of_known_new_IP_data, unknown_IP_flows):
    absolute_data, IPs_in_abs_file = open_sort_abs_file(e)
    new_absolute_file_flows = []
    new_absolute_file_flows += absolute_data
    unknown_IP_flows_new = []
    for new_flow2 in unknown_IP_flows:
        new_flow2.extend([new_flow2[1]])
        unknown_IP_flows_new.append(new_flow2)
    new_absolute_file_flows.extend(unknown_IP_flows_new)
    if not list_of_known_new_IP_data:
        pass
    else:
        for x1, new_flow in enumerate(list_of_known_new_IP_data):
            for x2, absolute_flow in enumerate(new_absolute_file_flows):
                if absolute_flow[0] == new_flow[0]:
                    days_since_first_seen = (current_time - float(absolute_flow[9])) // 86400.0
                    if days_since_first_seen != 0:
                        updated_event_average = ((float(absolute_flow[10])) * (days_since_first_seen - 1) + float(
                            new_flow[1])) / days_since_first_seen
                    else:
                        updated_event_average = ((float(absolute_flow[10])) * (days_since_first_seen - 1) + float(
                            new_flow[1])) / 1

                    updated_total_events = float(new_flow[1]) + float(absolute_flow[1])
                    updated_total_duration = float(absolute_flow[2]) + float(new_flow[2])
                    updated_average_duration = (float(absolute_flow[3]) + float(new_flow[3])) / 2.0
                    updated_total_bytes = float(absolute_flow[4]) + float(new_flow[4])
                    updated_average_bytes = (float(absolute_flow[5]) + float(new_flow[5])) / 2.0
                    updated_total_packets = float(absolute_flow[6]) + float(new_flow[6])
                    updated_average_packets = (float(absolute_flow[7]) + float(new_flow[7])) / 2.0
                    updated_last_event = new_flow[9]

                    updated_entry = [new_flow[0], updated_total_events, updated_total_duration,
                                     updated_average_duration,
                                     updated_total_bytes, updated_average_bytes, updated_total_packets,
                                     updated_average_packets,
                                     absolute_flow[8], updated_last_event, updated_event_average]
                    new_absolute_file_flows[x2] = updated_entry
                    break
                else:
                    continue
    with open(current_directory + '/Main/ASN/strings_to_check.csv', 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        list_of_good_organiations = list(csv_reader)
    asn_info = get_ASN_data(current_directory + '/Main/ASN/GeoLite2-ASN.mmdb', new_absolute_file_flows)
    whitelisted_nets, whitelisted_ips = load_whitelist()
    list_of_FPs = []
    for index, flow in enumerate(new_absolute_file_flows):
        judgement1 = check_if_ip_is_in_whitelisted_nets(flow[0], whitelisted_nets)
        judgement2 = check_if_ip_is_in_whitelisted_ips(flow[0], whitelisted_ips)
        judgement3, entry = check_organization_strings(asn_info[flow[0]], list_of_good_organiations)
        if judgement1 == True:
            list_of_FPs.append(flow)
            del new_absolute_file_flows[index]
            with open(AIPP_direcory + "/log.txt", "a") as myfile:
                myfile.write('Found ' + str(flow[0]) + ' in Whitelisted Nets. Deleting entry...' + "\n")
        elif judgement2 == True:
            list_of_FPs.append(flow)
            del new_absolute_file_flows[index]
            with open(AIPP_direcory + "/log.txt", "a") as myfile:
                myfile.write('Found ' + str(flow[0]) + ' in Whitelisted IPs. Deleting entry...' + "\n")
        elif judgement3 == True:
            list_of_FPs.append(flow)
            del new_absolute_file_flows[index]
            with open(AIPP_direcory + "/log.txt", "a") as myfile:
                myfile.write('Found ' + str(flow[0]) + ' ASN matches organization ' + str(entry) + ' Deleting entry...' + "\n")
        else:
            continue
    with open(FP_log_file, 'a') as FP_file:
        csvwriter = csv.writer(FP_file)
        csvwriter.writerows(list_of_FPs)
    with open(e, 'w') as new_file_another:
            wr2 = csv.writer(new_file_another, quoting=csv.QUOTE_ALL)
            for y in new_absolute_file_flows:
                wr2.writerow(y)


def create_final_blacklist(path_to_file, data_from_absolute_file, function_to_use, aip_direcory):
    with open(path_to_file, 'wt', newline ='') as new_file2:
        writer = csv.DictWriter(new_file2, fieldnames=['# Top IPs from data gathered in last 24 hours only', date])
        writer.writeheader()
        writer1 = csv.DictWriter(new_file2, fieldnames=['Number', 'IP address', 'Rating'])
        writer1.writeheader()
        if function_to_use == getattr(linear_models, list_of_functions_that_were_choosen[1]):
            with open(aip_direcory + "log.txt", "a") as myfile:
                myfile.write('Using Prioritize New Function')
            for x2, interesting_rating2 in enumerate(sort_data_decending(function_to_use(data_from_absolute_file, current_time, path_aging_modifier_pn))):
                if float(interesting_rating2[1]) >= 0.002:
                    new_entry = {'Number': x2, 'IP address': list(interesting_rating2)[0], 'Rating': interesting_rating2[1]}
                    writer1.writerows([new_entry])
                else:
                    break
        elif function_to_use == getattr(linear_models, list_of_functions_that_were_choosen[0]):
            with open(aip_direcory + "log.txt", "a") as myfile:
                myfile.write('Using Prioritize Consistent Function')
            for x2, interesting_rating2 in enumerate(sort_data_decending(function_to_use(data_from_absolute_file, current_time, path_aging_modifier_pc))):
                if float(interesting_rating2[1]) >= 0.057:
                    new_entry = {'Number': x2, 'IP address': list(interesting_rating2)[0],
                                 'Rating': interesting_rating2[1]}
                    writer1.writerows([new_entry])
                else:
                    break
        else:
            with open(aip_direcory + "log.txt", "a") as myfile:
                myfile.write('Using Only New IPs Function')
            for x2, interesting_rating2 in enumerate(sort_data_decending(function_to_use(data_from_absolute_file, current_time, path_aging_modifier_pc))):
                new_entry = {'Number': x2, 'IP address': list(interesting_rating2)[0],
                             'Rating': interesting_rating2[1]}
                writer1.writerows([new_entry])


# Now call all the functions on the data

list_of_known_data_flows, list_of_known_IPs_in_data = open_sort_abs_file(record_file_path_for_absolute_data)

list_of_new_data_flows, list_of_IPs_in_new_data = open_sort_new_file_linear(folder_path_for_raw_Splunk_data, new_data_files)

unknown_IP_flows_from_new_data, unknown_IPs_from_new_data, known_IP_data_flows_from_new_data, known_IPs_from_new_data\
    = sort_IPs_from_data(list_of_known_IPs_in_data, list_of_new_data_flows)

write_unkown_IPs_to_data_file(unknown_IPs_from_new_data, record_file_path_to_known_IPs)

update_records_files(record_file_path_for_absolute_data, known_IP_data_flows_from_new_data, unknown_IP_flows_from_new_data)

number_of_lines = len(open(record_file_path_for_absolute_data).readlines())
with open(AIPP_direcory + "/log.txt", "a") as myfile:
    myfile.write('Number of lines in absolute data' + str(number_of_lines) + "\n")


# Pull the three functions that were choosen by the user from the dictionary of functions.
# print(list_of_functions_that_were_choosen)

PCF = getattr(linear_models, list_of_functions_that_were_choosen[0])
PNF = getattr(linear_models, list_of_functions_that_were_choosen[1])
OTF = getattr(linear_models, list_of_functions_that_were_choosen[2])

# Call the create blacklist function for each of the three user input functions
create_final_blacklist(top_IPs_for_all_time, get_updated_flows(record_file_path_for_absolute_data), PCF, AIPP_direcory)
create_final_blacklist(top_IPs_all_time_newer_prioritized, get_updated_flows(record_file_path_for_absolute_data), PNF, AIPP_direcory)
create_final_blacklist(top_IPs_seen_today, unknown_IP_flows_from_new_data, OTF, AIPP_direcory)


shutil.copy2(record_file_path_to_known_IPs, traditional_blacklist)

with open(AIPP_direcory + "/log.txt", "a") as myfile:
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


input_data = '/home/the-shadow/Data/2021-02-01_labelled_raw.csv'
prediction_data = '/home/the-shadow/Data/Absolute_Data.csv'
output = '/home/the-shadow/Data/ML-Blacklist.csv'

# Process the training data
data = load_data(input_data)
data = add_row(data)
y_all, X_all = separate_labels_data(data)
X_train, X_test, y_train, y_test = bin_data(y_all, X_all)

# Process the data we will be predicting on
processed_data = process_old_data(prediction_data)
list_of_new_data_flows, ips_in_data = open_sort_new_file(prediction_data)

# Train a model and find good paramaters
best_params = find_best_param(X_train, X_test, y_train, y_test)

# Train a model using best params, using the whole dataset this time
predictions = train_on_complete_data(X_all, y_all, processed_data, best_params)

blacklist = create_blacklist(predictions, list_of_new_data_flows)

write_blacklist_to_file(output, blacklist)

print('Number of BL IPs: ', len(blacklist))
