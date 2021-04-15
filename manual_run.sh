#!/bin/bash
answer1="Yes"
answer2="No"
answer3="1"
answer4="2"

echo "............................"
echo "Please Select a option from the menu[1,2]:"
echo "(1) New Instance, create ouput folder and folders"
echo "(2) Running Instance, save output to an existing folder"
read option
echo "............................"

echo "Location of input data files(Can contain one or more files):"
read input_data_folder
echo "............................"

while [ ! -d $input_data_folder ]
do
   echo Not a real directory, please input a real one:
   read input_data_folder
   echo ............................
done

if [ "$option" = "$answer3" ]
then
		echo New Directory where you want results, no slash at end:
		read output_folder
		echo ............................
		# Check to see if the directory is real.
		while [ ! -d $output_folder ]
		do
			echo Not a real directory, do you wish to create it? [Yes,No]
			read answer
		  if [ "$answer" = "$answer1" ]
		  then
		  	mkdir $output_folder
				mkdir $output_folder/Input_Data/
				mkdir $output_folder/Historical_Ratings/
				mkdir $output_folder/Historical_Ratings/Prioritize_Consistent/
				mkdir $output_folder/Historical_Ratings/Prioritize_New/
				mkdir $output_folder/Historical_Ratings/Seen_today_Only/
				mkdir $output_folder/Historical_Ratings/Traditional/
				mkdir $output_folder/Historical_Ratings/Random_Forest_Aggregated/
				mkdir $output_folder/Historical_Ratings/Random_Forest_Concatinated/
				mkdir $output_folder/ML_Model_Data/
				touch $output_folder/ML_Model_Data/aggregate_data_labeled.csv
				touch $output_folder/ML_Model_Data/aggregate_data.csv
				touch $output_folder/ML_Model_Data/new_24_hour_data.csv
				touch $output_folder/ML_Model_Data/previous_24_hour_data.csv
				touch $output_folder/ML_Model_Data/previous_24_hour_data_labeled.csv
				touch $output_folder/ML_Model_Data/concatinated_data_labeled.csv
				touch $output_folder/ML_Model_Data/temp.csv
				touch $output_folder/Absolute_Data.csv
				touch $output_folder/Known_IPs.txt
				touch $output_folder/Processed_Splunk_Files.txt
				touch $output_folder/Times.csv
				touch $output_folder/Selected_modules.csv
				touch $output_folder/FP_log_file.csv
				touch $output_folder/log.txt
        touch $output_folder/Aging-modifiers-pc.csv
        touch $output_folder/Aging-modifiers-pn.csv
		  elif [ "$answer" = "$answer2" ]
		  then
		  	echo Input different location:
		  	read output_folder
				mkdir $output_folder/Historical_Ratings/
				mkdir $output_folder/Input_Data/
				mkdir $output_folder/Historical_Ratings/Prioritize_Consistent/
				mkdir $output_folder/Historical_Ratings/Prioritize_New/
				mkdir $output_folder/Historical_Ratings/Seen_today_Only/
				mkdir $output_folder/Historical_Ratings/Traditional/
				mkdir $output_folder/Historical_Ratings/Random_Forest_Aggregated/
				mkdir $output_folder/Historical_Ratings/Random_Forest_Concatinated/
				mkdir $output_folder/ML_Model_Data/
				touch $output_folder/ML_Model_Data/aggregate_data_labeled.csv
				touch $output_folder/ML_Model_Data/aggregate_data.csv
				touch $output_folder/ML_Model_Data/new_24_hour_data.csv
				touch $output_folder/ML_Model_Data/previous_24_hour_data.csv
				touch $output_folder/ML_Model_Data/previous_24_hour_data_labeled.csv
				touch $output_folder/ML_Model_Data/concatinated_data_labeled.csv
				touch $output_folder/ML_Model_Data/temp.csv
				touch $output_folder/Absolute_Data.csv
				touch $output_folder/FP_log_file.csv
				touch $output_folder/log.txt
				touch $output_folder/Known_IPs.txt
				touch $output_folder/Processed_Splunk_Files.txt
				touch $output_folder/Times.csv
				touch $output_folder/Selected_modules.csv
		  else
		  	continue
			echo ............................
		  fi
		done
elif [ "$option" = "$answer4" ]
then
	echo "Please Input location of current instance output files:"
	read output_folder
fi


# Export all variables so they can be accessed by AIP.py
export output_folder
export input_data_folder


directory_of_AIP=$(dirname $(readlink -f "manual_run.sh"))

python3 $directory_of_AIP/Main/select_linear_models.py

for entry in $input_data_folder/*
do
   # Copy the aggregated data from the previous run to the ML model folder. This is the data for the aggregate ml model that
   # needs to be labeled with the new data file, and then used for training.
   cp $output_folder/Absolute_Data.csv $output_folder/ML_Model_Data/aggregate_data.csv
#   Copy the current new data file to the ML model folder, overridding the previous one. This will be used to label the aggregated data for the aggregated model,
#   and used to label the previous unlabeled day data for the concatination model.
   cp $entry $output_folder/ML_Model_Data/new_24_hour_data.csv
   # Copy the current new data file to the input Data folder. This is not labeled, coming directly from the argus data
   cp $entry $output_folder/Input_Data/
   echo $entry >> $output_folder/log.txt
   echo $entry
#   Run the label data script. This will:
#   1) Label the previous aggregated data using the new data file
#   2) Label the previous new data file using the current new data file, and append this to the end of the historical
#   concatinated_data_labeled file.
   if [ ! -s "$output_folder/ML_Model_Data/aggregate_data.csv" ]
   then
        echo No past data yet, skipping ML models to next time
   else
        echo labeling data ....
        $directory_of_AIP/Main/ML-Model/label_data.sh
        echo finished .....
   fi
#   run AIP. This will:
#   1) Find the new file in the input directory
#   2) Aggregate this new data with the historical data
#   3) Run the Linear models on the updated historical data
#   4) Train and run the two Random Forest models using the labeled aggregated data and the labeled concatinated data
   python3 $directory_of_AIP/Main/AIP.py
#   Save the new_data.csv file to previous_unlabeled_data.csv, so that it can be used in the next run
   cp $output_folder/ML_Model_Data/new_24_hour_data.csv $output_folder/ML_Model_Data/previous_24_hour_data.csv
#   Remove the current new data file from the folder. This is so that next this script is run, we dont loop thrpugh all the
#   data files again
   rm $entry
done
