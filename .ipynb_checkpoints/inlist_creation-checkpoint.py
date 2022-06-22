import numpy as np
import os
import sys

def write_inlist(base_inlist, new_inlist_file, parameter_names, parameter_values, inlist_number, storage_directory='/mnt/sdb3/neutron_star_code_data/basic_run/training_grid/'):

    new_inlist = open(new_inlist_file, 'w')

    base_inlist.seek(0)

    for line in base_inlist.readlines():

        parameter_line = False
        for i, parameter_name in enumerate(parameter_names):
            if line[:7+len(parameter_name)] == '    {} = '.format(parameter_name):
                new_inlist.write('    {} = {}\n'.format(parameter_name, parameter_values[i]))
                parameter_line = True
                break

        if parameter_line == True:
            continue

        elif line[:23] == '    output_directory = ':
            new_inlist.write("\n    output_directory = '{}LOGS{:04d}'\n".format(storage_directory, inlist_number))

        # If it is not one of the lines to change, then copy it to each new inlist.
        else:
            new_inlist.write(line)

    new_inlist.close()

def create_inlist_set(set_parameters, parameter_names, storage_directory, base_inlist_file='base_inlist'):
    # Open a base inlist that includes all parameters that will stay constant across all runs.
    # We will add the variable parameters to this inlist.
    base_inlist = open(base_inlist_file, 'r')

    # Iterate through each set of parameter values for all models.
    for i, parameter_values in enumerate(set_parameters):

        # Create a numbered LOGS directory in which to save the inlist and where the LOGS files will go.
        LOGS_directory = '{}LOGS{:04d}/'.format(storage_directory, i)
        try:
            os.mkdir(LOGS_directory)
        except FileExistsError:
            pass

        # Create a new file to write the inlist based on the base_inlist.
        new_inlist_file = '{}inlist{:04d}'.format(LOGS_directory, i)
        write_inlist(base_inlist, new_inlist_file, parameter_names, parameter_values, i)

    # After creating all inlists, close the base_inlist.
    base_inlist.close()

# Set home and dStar directories.
home_directory = os.getenv('HOME')
dStar_directory = home_directory + '/dStar/'
base_inlist_file = 'base_inlist'

# Location to store all the training LOGS directories
training_directory = home_directory + 'Storage/Neutron\ Stars/neutron_star_code/basic_run/training_grid/'
try:
    os.mkdir(training_directory)
except FileExistsError:
    pass

testing_directory = home_directory + 'Storage/Neutron\ Stars/neutron_star_code/basic_run/testing_grid/'
# Create the directory if is does not already exist.
try:
    os.mkdir(testing_directory)
except FileExistsError:
    pass

# Name of file containing ranges of parameters for the grid
parameter_file = 'parameter_ranges'
# Load names of parameters that will be varied.
parameter_names = np.loadtxt(parameter_file, usecols=0, dtype=str)
# Columns 1-3 contain numbers in the same format as a np.linspace argument:
# core_mass 1.4 2.0 11 will produce an array np.linspace(1.4, 2.0, 11) representing the core_mass values that we include in our grid.
min_values, max_values, num_parameter_values = np.loadtxt('parameter_ranges', usecols=(1,2,3), unpack=True)

# The number of different parameter values for each parameter
num_parameter_values = num_parameter_values.astype(int)
# We will produce a model for every combination of parameter values.
# The total number of models will be the product of the number of parameter values.
total_num_models = np.prod(num_parameter_values)

# A list to store the ranges of parameter values.
# Store as a list rather than an array to allow different parameters to have different numbers of values.
parameter_ranges = []

for i in range(len(parameter_names)):
    parameter_ranges.append(np.linspace(min_values[i], max_values[i], num_parameter_values[i]))

training_parameter_grid = np.zeros((total_num_models, len(parameter_names)))

for model_number, indices in enumerate(np.ndindex(tuple(num_parameter_values))):

    # The array of parameters for this particular model
    parameter_values = training_parameter_grid[model_number]

    # Iterate through each parameter and assign its value
    for i, parameter_value in enumerate(parameter_values):
        # The indices in order correspond to each parameter that we want to assign
        # so for the ith parameter value, we find the ith parameter range array,
        # then use the ith index to determine which value in that array to assign
        parameter_values[i] = parameter_ranges[i][indices[i]]

for i, parameter_values in enumerate(training_parameter_grid):

    LOGS_directory = '{}LOGS{:04d}/'.format(training_directory, i)
    try:
        os.mkdir(LOGS_directory)
    except FileExistsError:
        pass

    new_inlist_file = '{}inlist{:04d}'.format(LOGS_directory, i)

    write_inlist(base_inlist, new_inlist_file, parameter_names, parameter_values, i)

testing_parameter_grid = np.zeros_like(training_parameter_grid)

for testing_model in training_parameter_grid:
    for i in range(len(parameter_names)):
        testing_model[i] = np.random.uniform(low=min_values[i], high=max_values[i])

base_inlist.close()

print(total_num_models)
