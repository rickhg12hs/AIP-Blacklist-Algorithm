#!/bin/bash
echo ............................
echo Directory where you want results, no slash at end:
read output_folder_directory
echo ............................

# Check to see if the directory is real.
while [ ! -d $output_folder_directory ]
do
   echo Not a real directory, please input a real one:
   read output_folder_directory
   echo ............................
done

# Input a name that you want for these results
echo Pick a name that does not already exist for your results folder:
read name_of_results_folder
echo ............................

# Check to see if directory already exists.
while [ -d $output_folder_directory/$name_of_results_folder ]
do
   echo Directory alreay exists, please name it something else:
   read name_of_results_folder
   echo ............................
done

echo Path to input data folder:
read input_data_folder
echo ............................

# Check to see if the directory is real.
while [ ! -d $input_data_folder ]
do
   echo Not a real directory, please input a real one:
   read input_data_folder
   echo ............................
done

echo Path to evaluation data:
echo Note: In order to evaluate all blacklists generated from input data, eval
echo data should contain one more days data file that input data:
read eval_data_folder

# Check to see if the directory is real.
while [ ! -d $eval_data_folder ]
do
   echo Not a real directory, please input a real one:
   read eval_data_folder
   echo ............................
done

directory_of_AIP=$(pwd)

output_folder=$output_folder_directory/$name_of_results_folder
mkdir $output_folder/
mkdir $output_folder/Historical_Ratings/
mkdir $output_folder/Evaluations/
touch $output_folder/Evaluations/averages.csv
touch $output_folder/Evaluations/all_percentages.csv
mkdir $output_folder/Historical_Ratings/Prioritize_Consistent/
mkdir $output_folder/Historical_Ratings/Prioritize_New/
mkdir $output_folder/Historical_Ratings/Seen_today_Only/
mkdir $output_folder/Historical_Ratings/Traditional/
touch $output_folder/Absolute_Data.csv
touch $output_folder/Known_IPs.txt
touch $output_folder/Processed_Splunk_Files.txt
touch $output_folder/Times.csv
touch $output_folder/Selected_modules.csv

# Export all variables so they can be accessed by AIP.py
export output_folder
export prioritize_consistent
export prioritize_new
export only_todays_ips
export eval_data_folder
export input_data_folder

python3 $directory_of_AIP/Main/Select_Modules.py
python3 $directory_of_AIP/Main/AIP.py

# for entry in ~/Test/Data_From_Splunk/*
# do
#   cp "$entry" /home/thomas/Test/Gradual/B20-E20/Out-Put-Files/Input-Data/
#   echo "$entry"
#   python3 /home/thomas/Test/Gradual/B20-E20/AIP.py
# done
#
# python3 /home/thomas/Test/Gradual/B20-E20/Eval/Eval-Main1.1.py