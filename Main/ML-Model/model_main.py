from load_data import *
from train_model import *

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
list_of_new_data_flows, list_of_IPs_in_new_data = open_sort_new_file(prediction_data)

# Train a model and find good paramaters
best_params = find_best_param(X_train, X_test, y_train, y_test)

# Train a model using best params, using the whole dataset this time
predictions = train_on_complete_data(X_all, y_all, processed_data, best_params)

blacklist = create_blacklist(predictions, list_of_new_data_flows)

write_blacklist_to_file(output, blacklist)

print('Number of BL IPs: ', len(blacklist))












