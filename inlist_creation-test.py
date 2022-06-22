import numpy as np
import os
import sys

def make_directory(directory_name):
    try:
        os.mkdir(directory_name)
    except FileExistsError:
        pass

def write_inlist(base_inlist, new_inlist_file, parameter_names, parameter_values, LOGS_directory):

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
            new_inlist.write("\n    output_directory = '{}'\n".format(LOGS_directory))

        # If it is not one of the lines to change, then copy it to each new inlist.
        else:
            new_inlist.write(line)

    new_inlist.close()

def create_inlist_set(set_parameters, parameter_names, inlist_directory, LOGS_directories, base_inlist_file='base_inlist'):
    # Open a base inlist that includes all parameters that will stay constant across all runs.
    # We will add the variable parameters to this inlist.
    base_inlist = open(base_inlist_file, 'r')

    # Iterate through each set of parameter values for all models.
    for i, parameter_values in enumerate(set_parameters):

        # Create a numbered LOGS directory in which to save the inlist and where the LOGS files will go.
        LOGS_directory = '{}LOGS{:04d}/'.format(LOGS_directories, i)
        make_directory(LOGS_directory)

        # Create a new file to write the inlist based on the base_inlist.
        new_inlist_file = '{}inlist{:04d}'.format(inlist_directory, i)
        write_inlist(base_inlist, new_inlist_file, parameter_names, parameter_values, LOGS_directory)

    # After creating all inlists, close the base_inlist.
    base_inlist.close()

# Set home and dStar directories.
home_directory = os.getenv('HOME')
dStar_directory = home_directory + '/dStar/'
base_inlist_file = 'base_inlist'

# Create directories in which to store training and testing inlists and training and testing LOGS.
training_inlists_directory = 'training_inlists/'
testing_inlists_directory = 'testing_inlists/'
training_LOGS_directories = '{}/Storage/Research/neutron_star_code/basic_run/training_LOGS/'.format(home_directory)
testing_LOGS_directories = '{}/Storage/Research/neutron_star_code/basic_run/testing_LOGS/'.format(home_directory)

make_directory(training_inlists_directory)
make_directory(testing_inlists_directory)
make_directory(training_LOGS_directories)
make_directory(testing_LOGS_directories)

# Create the grid of parameters for the training set.

# Name of file containing ranges of parameters for the grid
parameter_file = 'parameter_ranges'
# Load names of parameters that will be varied.
parameter_names = np.loadtxt(parameter_file, usecols=0, dtype=str)

np.save('parameter_names.npy', parameter_names)
# Columns 1-3 contain numbers in the same format as a np.linspace argument:
# core_mass 1.4 2.0 11 will produce an array np.linspace(1.4, 2.0, 11) representing the core_mass values that we include in our grid.
min_values, max_values, num_parameter_values = np.loadtxt('parameter_ranges', usecols=(1,2,3), unpack=True)

# The number of different parameter values for each parameter
num_parameter_values = num_parameter_values.astype(int)
# We will produce a model for every combination of parameter values.
# The total number of models will be the product of the number of parameter values.
total_num_models = np.prod(num_parameter_values)

# A list to store the ranges of parameter values.
# Store as a list rather than an array because different parameters may have different numbers of values so the second dimension will not necessarily be the same size for all elements.
parameter_ranges = []

for i in range(len(parameter_names)):
    parameter_ranges.append(np.linspace(min_values[i], max_values[i], num_parameter_values[i]))

training_parameters = np.zeros((total_num_models, len(parameter_names)))

for model_number, indices in enumerate(np.ndindex(tuple(num_parameter_values))):

    # The array of parameters for this particular model
    parameter_values = training_parameters[model_number]

    # Iterate through each parameter and assign its value
    for i, parameter_value in enumerate(parameter_values):
        # The indices in order correspond to each parameter that we want to assign
        # so for the ith parameter value, we find the ith parameter range array,
        # then use the ith index to determine which value in that array to assign
        parameter_values[i] = parameter_ranges[i][indices[i]]

np.save('training_parameters.npy', training_parameters)

create_inlist_set(training_parameters, parameter_names, training_inlists_directory, training_LOGS_directories)

# Create testing set of parameters.

testing_parameters = np.zeros_like(training_parameters)

for i in range(testing_parameters.shape[0]):
    for j in range(testing_parameters.shape[1]):
        testing_parameters[i, j] = np.random.uniform(low=min_values[j], high=max_values[j])

np.save('testing_parameters.npy', testing_parameters)

create_inlist_set(testing_parameters, parameter_names, testing_inlists_directory, testing_LOGS_directories)

print(total_num_models)
