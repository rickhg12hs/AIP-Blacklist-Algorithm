#!/bin/bash -e

echo $output_folder

aggregate_data_labeled=$output_folder/ML_Model_Data/aggregate_data_labeled.csv
aggregate_data=$output_folder/ML_Model_Data/aggregate_data.csv
new_24_hour_data=$output_folder/ML_Model_Data/new_24_hour_data.csv
previous_24_hour_data=$output_folder/ML_Model_Data/previous_24_hour_data.csv
previous_24_hour_data_labeled=$output_folder/ML_Model_Data/previous_24_hour_data_labeled.csv
concatinated_data_labeled=$output_folder/ML_Model_Data/concatinated_data_labeled.csv
temp=$output_folder/ML_Model_Data/temp.csv

rm $aggregate_data_labeled
# First, we will label the aggregate_data_to_be_labeled using the new_unlabed_data_for_labeling,
# and store it to labeled_aggregate_data

# Clear the labeled_aggregate_data file so that all the labeles are fresh

for line in $(cat $aggregate_data);
do
	if [[ $line =~ "SrcAddr" ]]; then
		echo $line",Label" >> $aggregate_data_labeled
	else
		IP=$(echo $line|awk -F, '{print $1}')
		if grep "$IP" $new_24_hour_data; then
			line="${line},1"
			echo $line >> $aggregate_data_labeled
		else
			line="${line},0"
			echo $line >> $aggregate_data_labeled
		fi
	fi
done

# Fix the ^M error in data file
sed 's/\r//' $aggregate_data_labeled > $temp
cp $temp $aggregate_data_labeled
rm $temp
touch $temp

# Now, we will label the previous_unlabeled_data using the new_unlabed_data_for_labeling,
# and then append this data to the historical_concatinated_data

if [ ! -s "$concatinated_data_labeled" ]
   then
        for line in $(cat $previous_24_hour_data);
            do
              if [[ $line =~ "SrcAddr" ]]; then
                echo $line",Label" >> $previous_24_hour_data_labeled
              else
                IP=$(echo $line|awk -F, '{print $1}')
                if grep "$IP" $new_24_hour_data; then
                  line="${line},1"
                  echo $line >> $previous_24_hour_data_labeled
                else
                  line="${line},0"
                  echo $line >> $previous_24_hour_data_labeled
                fi
              fi
            done
   else
        for line in $(cat $previous_24_hour_data);
            do
              if [[ $line =~ "SrcAddr" ]]; then
                echo skipping labels
              else
                IP=$(echo $line|awk -F, '{print $1}')
                if grep "$IP" $new_24_hour_data; then
                  line="${line},1"
                  echo $line >> $previous_24_hour_data_labeled
                else
                  line="${line},0"
                  echo $line >> $previous_24_hour_data_labeled
                fi
              fi
            done
   fi

# Fix the ^M error in data file
sed 's/\r//' $previous_24_hour_data_labeled > $temp
cp $temp $previous_24_hour_data_labeled
rm $temp
touch $temp

