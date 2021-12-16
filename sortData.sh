#!/bin/bash

python concatData.py

mkdir lengths
mkdir finalMeasuredImage_dilated
mkdir runvalues

mv *ues.csv runvalues/
mv *ate.png finalMeasuredImage_dilated/
mv *lengths.csv lengths/
mv *Lengths.csv lengths/

# i=0                                       # Reset a counter
# for filename in ./lengths/*_lengths.csv; do 
# 	OutFileName="${filename%Sol_*}_allLengths.csv" 	## "%UV_*" if UV, "%Sol_*"
# 	if [[ $i -eq 0 ]] ; then 
# 		head -1  "$filename" >   "$OutFileName" # Copy header if it is the first file
# 	fi
# 	tail -n +2  "$filename" >>  "$OutFileName" # Append from the 2nd line each file
# 	i=$(( $i + 1 ))                            # Increase the counter
# done


# For loop dapted from the stach exhange answere here: 
# https://stackoverflow.com/questions/24641948/merging-csv-files-appending-instead-of-merging/24643455
# Edited to use the filenames in the directory to generate the output filename