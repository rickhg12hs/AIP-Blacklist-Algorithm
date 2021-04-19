from inspect import getmembers, isfunction
import linear_models
import pandas as pd
import csv
from sklearn.model_selection import train_test_split
import operator
import os
from datetime import datetime

def list_method_A_functions():
    functions_list = [o[0] for o in getmembers(linear_models) if isfunction(o[1])]
    dictionary_of_options = {}
    running_total = 1
    for function in functions_list:
        if function[:21] == 'prioritize_consistent':
            print(running_total, ':', function)
            dictionary_of_options[running_total] = function
            running_total += 1
    return dictionary_of_options

def list_method_B_functions():
    functions_list = [o[0] for o in getmembers(linear_models) if isfunction(o[1])]
    running_total = 1
    dictionary_of_options = {}
    for function in functions_list:
        if function[:14] == 'prioritize_new':
            print(running_total, ':', function)
            dictionary_of_options[running_total] = function
            running_total += 1
    return dictionary_of_options

def list_method_C_functions():
    functions_list = [o[0] for o in getmembers(linear_models) if isfunction(o[1])]
    running_total = 1
    dictionary_of_options = {}
    for function in functions_list:
        if function[:15] == 'todays_ips_only':
            print(running_total, ':', function)
            dictionary_of_options[running_total] = function
            running_total += 1
    return dictionary_of_options

def combine_data_pandas(data1, data2):
    frames = [data1, data2]
    df_12 = pd.concat(frames)
    return df_12


def load_data(csv_data_file):
    data = pd.read_csv(csv_data_file, header='infer')
    return data

def add_row(data):
    data['attack_duration'] = data.last_event_time - data.first_event_time
    return data

def process_old_data(csv_data_file):
    data = pd.read_csv(csv_data_file, header='infer')
    data['attack_duration'] = data.last_event_time - data.first_event_time
    X_all = data.loc[:, ~data.columns.isin(['AV_Events', 'SrcAddr'])]
    return X_all

def extract_ips_from_pandas_dataframe(dataframe):
    ips = dataframe['SrcAddr'].tolist()
    return ips

def separate_labels_data(data):
    y_all = data.Label
    X_all = data.loc[:, ~data.columns.isin(['Label', 'SrcAddr'])]
    return y_all, X_all

def bin_data(y_all, X_all):
    X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size=0.33, random_state=42)
    return X_train, X_test, y_train, y_test

def open_sort_new_file(file):
    list_of_new_data_flows = []
    list_of_IPs_in_new_data = []
    with open(file, 'r') as csvfile:
        for line in csv.reader(csvfile):
            if line[0] != 'SrcAddr':
                list_of_new_data_flows.append([line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9]])
                list_of_IPs_in_new_data.append(line[0])
            else:
                continue
    return list_of_new_data_flows, list_of_IPs_in_new_data

def write_blacklist_to_file(path_to_file, blacklist_ips):
    with open(path_to_file, 'wt', newline ='') as new_file2:
        writer = csv.DictWriter(new_file2, fieldnames=['# RandomForest Blacklist'])
        writer.writeheader()
        writer1 = csv.DictWriter(new_file2, fieldnames=['IP address'])
        writer1.writeheader()
        for number, ip in enumerate(blacklist_ips):
            new_entry = {'IP address': ip}
            writer1.writerows([new_entry])

def open_sort_new_file_linear(b, list_of_new_files):
    list_of_new_data_flows = []
    list_of_IPs_in_new_data = []
    for file in list_of_new_files:
        with open(b + '/' + file, 'r') as csvfile:
            for line in csv.reader(csvfile):
                if line[0] != 'SrcAddr':
                    list_of_new_data_flows.append([line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9]])
                    list_of_IPs_in_new_data.append(line[0])
                else:
                    continue
    return list_of_new_data_flows, list_of_IPs_in_new_data


def open_sort_abs_file(e):
    IP_flows = []
    IPs_in_absolute_file = []
    with open(e, 'r') as csvfile:
        for line in csv.reader(csvfile):
            if not line:
                break
            elif line[0] == 'SrcAddr':
                continue
            else:
                IP_flows.append([line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10]])
                IPs_in_absolute_file.append(line[0])
    return IP_flows, IPs_in_absolute_file

def get_updated_flows(location_of_absolute_data_file):
    IP_flows = []
    with open(location_of_absolute_data_file, 'r') as csvfile:
        for line in csv.reader(csvfile):
            if not line:
                break
            elif line[0] == 'SrcAddr':
                continue
            else:
                IP_flows.append([line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10]])
    return IP_flows

def sort_IPs_from_data(IPs_from_absolute_data, IP_flows_from_todays_data):
    unknown_IP_flows = []
    unknown_IPs = []
    known_IPs = []
    known_IP_data_flows = []
    for IP in IP_flows_from_todays_data:
        if IP[0] in IPs_from_absolute_data:
            known_IP_data_flows.append(IP)
            known_IPs.append(IP[0])
        elif IP[0] not in IPs_from_absolute_data:
            unknown_IP_flows.append(IP)
            unknown_IPs.append(IP[0])
    return unknown_IP_flows, unknown_IPs, known_IP_data_flows, known_IPs


def write_unkown_IPs_to_data_file(list_of_unknown_IPs, d):
    with open(d, 'a') as data_file:
        for flow in list_of_unknown_IPs:
            data_file.write(flow + '\n')

def sort_data_decending(data):
    list_as_dictionary = {}
    for entry in data:
        list_as_dictionary[entry[0]] = entry[1]
    return sorted(list_as_dictionary.items(), key=operator.itemgetter(1), reverse=True)


def create_final_blacklist(path_to_file, data_from_absolute_file, function_to_use, aip_direcory, date,
                           list_of_functions_that_were_choosen, current_time, path_to_aging_modifier):
    with open(path_to_file, 'wt', newline ='') as new_file2:
        writer = csv.DictWriter(new_file2, fieldnames=['# Top IPs from data gathered in last 24 hours only', date])
        writer.writeheader()
        writer1 = csv.DictWriter(new_file2, fieldnames=['Number', 'IP address', 'Rating'])
        writer1.writeheader()
        if function_to_use == getattr(linear_models, list_of_functions_that_were_choosen[1]):
            with open(aip_direcory + "log.txt", "a") as myfile:
                myfile.write('Using Prioritize New Function')
            for x2, interesting_rating2 in enumerate(sort_data_decending(function_to_use(data_from_absolute_file, current_time, path_to_aging_modifier))):
                if float(interesting_rating2[1]) >= 0.002:
                    new_entry = {'Number': x2, 'IP address': list(interesting_rating2)[0], 'Rating': interesting_rating2[1]}
                    writer1.writerows([new_entry])
                else:
                    break
        elif function_to_use == getattr(linear_models, list_of_functions_that_were_choosen[0]):
            with open(aip_direcory + "log.txt", "a") as myfile:
                myfile.write('Using Prioritize Consistent Function')
            for x2, interesting_rating2 in enumerate(sort_data_decending(function_to_use(data_from_absolute_file, current_time, path_to_aging_modifier))):
                if float(interesting_rating2[1]) >= 0.002:
                    new_entry = {'Number': x2, 'IP address': list(interesting_rating2)[0],
                                 'Rating': interesting_rating2[1]}
                    writer1.writerows([new_entry])
                else:
                    break
        else:
            with open(aip_direcory + "log.txt", "a") as myfile:
                myfile.write('Using Only New IPs Function')
            for x2, interesting_rating2 in enumerate(sort_data_decending(function_to_use(data_from_absolute_file, current_time, path_to_aging_modifier))):
                new_entry = {'Number': x2, 'IP address': list(interesting_rating2)[0],
                             'Rating': interesting_rating2[1]}
                writer1.writerows([new_entry])


def find_new_data_files(b, c, AIPP_direcory):
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