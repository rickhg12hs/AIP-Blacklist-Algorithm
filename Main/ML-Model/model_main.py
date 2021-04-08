import os
import csv
import datetime
import argparse
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
import numpy as np
from datetime import datetime
import time
from load_data import *
from train_model import *

input_data = '/home/the-shadow/Data/Labeled-Data/2021-02-01_labelled_raw.csv'
prediction_data = '/home/the-shadow/Data/Absolute_Data.csv'

# Process the training data
data = load_data(input_data)
data = add_row(data)
y_all, X_all = separate_labels_data(data)
X_train, X_test, y_train, y_test = bin_data(y_all, X_all)

# Process the data we will be predicting on
no_label_data = load_data(prediction_data)
processed_data = add_row_delete_row(no_label_data)
list_of_new_data_flows, list_of_IPs_in_new_data = open_sort_new_file(prediction_data)

# print(processed_data)

# Train a model and find good paramaters
# best_params = find_best_param(X_train, X_test, y_train, y_test)
#
# # Train a model using best params, using the whole dataset this time
# predictions = train_on_complete_data(X_all, y_all, no_label_data, best_params)
#
# # print('predictions: ', predictions)
# # print('list_of_new_data_flows: ', list_of_new_data_flows)
#
# blacklist = create_blacklist(predictions, list_of_new_data_flows)
#
# print('Number of BL IPs: ', len(blacklist))











