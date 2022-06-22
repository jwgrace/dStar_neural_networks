#!/bin/bash

# Save LOGS directories in a storage directory (to save space on SSD)
training_inlists_directory="training_inlists"
testing_inlists_directory="testing_inlists"
dStar_directory="/home/justin/dStar"

num_models=$(python3 inlist_creation-test.py)

# Run all training models.
for i in $(seq 0 $(($num_models - 1)))
    do
        inlist=$(printf $training_inlists_directory"/inlist%04d" $i)
        ./run_dStar -D $dStar_directory -I $inlist
    done

# Run all testing models.
for i in $(seq 0 $(($num_models - 1)))
    do
        inlist=$(printf $testing_inlists_directory"/inlist%04d" $i)
        ./run_dStar -D $dStar_directory -I $inlist
    done
