#!/bin/bash
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

# If we are going to create a new instance, we need to create all the needed record files
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
				mkdir $output_folder/Updated_Data_By_Day/
				touch $output_folder/Absolute_Data.csv
				touch $output_folder/Known_IPs.txt
				touch $output_folder/Processed_Splunk_Files.txt
				touch $output_folder/Times.csv
		  elif [ "$answer" = "$answer2" ]
		  then
		  	echo Input different location:
		  	read output_folder
				mkdir $output_folder/Input_Data/
				mkdir $output_folder/Updated_Data_By_Day/
				touch $output_folder/Absolute_Data.csv
				touch $output_folder/Known_IPs.txt
				touch $output_folder/Processed_Splunk_Files.txt
				touch $output_folder/Times.csv
		  else
		  	continue
			echo ............................
		  fi
		done
elif [ "$option" = "$answer4" ]
then
	echo "Please Input location of current instance ouput files:"
	read output_folder
fi

# Export all variables so they can be accessed by AIP.py
export output_folder
export input_data_folder

directory_of_AIP=$(dirname $(readlink -f "generate_absolute_data.sh"))

echo $directory_of_AIP

for entry in $input_data_folder/*
do
   cp "$entry" $output_folder/Input_Data/
   echo "$entry"
   python3 $directory_of_AIP/Main/update_historical_data.py
   cp $output_folder/Absolute_Data.csv $output_folder/Updated_Data_By_Day/`ls -1 $entry | grep -oP '[\d]+-[\d]+-[\d]+'`_data_file.csv
done