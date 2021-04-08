import pandas as pd
import csv
from sklearn.model_selection import train_test_split

def load_data(csv_data_file):
    data = pd.read_csv(csv_data_file, header='infer')
    return data

def add_row(data):
    data['attack_duration'] = data.last_event_time - data.first_event_time
    return data

def add_row_delete_row(data):
    data['attack_duration'] = data.last_event_time - data.first_event_time
    data.drop('AV_Events', axis=1)
    return data

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

