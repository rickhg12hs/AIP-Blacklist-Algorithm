#!/bin/bash -e

new_unlabed_data_for_labeling=$output_folder/ML_Model_Data/new_data.csv
aggregate_data_to_be_labeled=$output_folder/ML_Model_Data/temp_aggregate_data.csv
labeled_aggregate_data=$output_folder/ML_Model_Data/temp_aggregate_data_labeled.csv
previous_unlabeled_data_to_be_labled=$output_folder/ML_Model_Data/previous_unlabeled_data.csv
historical_concatinated_data=$output_folder/ML_Model_Data/concatinated_data_labeled.csv
temp=$output_folder/ML_Model_Data/temp.csv

# First, we will label the aggregate_data_to_be_labeled using the new_unlabed_data_for_labeling,
# and store it to labeled_aggregate_data

# Clear the labeled_aggregate_data file so that all the labeles are fresh
rm $labeled_aggregate_data

for line in $(cat $aggregate_data_to_be_labeled);
do
	if [[ $line =~ "SrcAddr" ]]; then
		echo $line",Label" >> $labeled_aggregate_data
	else
		IP=$(echo $line|awk -F, '{print $1}')
		if grep "$IP" $new_unlabed_data_for_labeling; then
			line="${line},1"
			echo $line >> $labeled_aggregate_data
		else
			line="${line},0"
			echo $line >> $labeled_aggregate_data
		fi
	fi
done

# Fix the ^M error in data file
sed 's/\r//' $labeled_aggregate_data > $temp
cp $temp $labeled_aggregate_data
rm $temp

# Now, we will label the previous_unlabeled_data using the new_unlabed_data_for_labeling,
# and then append this data to the historical_concatinated_data

for line in $(cat $previous_unlabeled_data);
do
	if [[ $line =~ "SrcAddr" ]]; then
		echo $line",Label" >> $temp
	else
		IP=$(echo $line|awk -F, '{print $1}')
		if grep "$IP" $new_unlabed_data_for_labeling; then
			line="${line},1"
			echo $line >> $temp
		else
			line="${line},0"
			echo $line >> $temp
		fi
	fi
done

cat $temp >> $historical_concatinated_data
