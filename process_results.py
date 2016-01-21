import json
import math
import sys
import os


def analyse_result_set():
    ## This function will go through all of the data files generated by data_collection.py,
    ## infer which tests have been run on which engines and so forth, and return a dictionary
    ## data structure to contain all of the data that will be extracted from those files.

    file_list = os.listdir('results/')
    tests = dict()

    for item in file_list:
        if os.path.isdir('results/' + item):
            tests[item] = dict()
            sub_file_list = os.listdir('results/' + item + '/')
            for data_file in sub_file_list:
                if data_file.endswith('.txt'):
                    if 'hhvm-benchmark' in data_file:
                        test_name = data_file.split('-')[0] + "-" + data_file.split('-')[1]
                        test_number = int((data_file.split('-')[2]).split('.')[0])
                        if not test_name in tests[item]:
                            tests[item][test_name] = dict()
                            tests[item][test_name]['num_tests'] = test_number
                        if tests[item][test_name]['num_tests'] < test_number:
                            tests[item][test_name]['num_tests'] = test_number
                    else:
                        test_name = data_file.split('-')[0]
                        test_number = int((data_file.split('-')[1]).split('.')[0])
                        if not test_name in tests[item]:
                            tests[item][test_name] = dict()
                            tests[item][test_name]['num_tests'] = test_number
                        if tests[item][test_name]['num_tests'] < test_number:
                            tests[item][test_name]['num_tests'] = test_number
    return tests


def byteify(input_string):
    # convert unicode strings to regular byte strings because fuck unicode
    if isinstance(input_string, dict):
        return {byteify(key):byteify(value) for key,value in input_string.iteritems()}
    elif isinstance(input_string, list):
        return [byteify(element) for element in input_string]
    elif isinstance(input_string, unicode):
        return input_string.encode('utf-8')
    else:
        return input_string


def get_data(filename):
    # load the json data from the output file, and return the object
    # de-unicodified
    if os.path.getsize(filename) == 0:
        return None

    with open(filename) as input_source:
        json_object = byteify(json.load(input_source))

    return json_object


def extract_data(test_name, engine_name, data_object, fields_to_extract, master_dictionary):
    # extracts the data that I am tracking from the output files, and adds it to the master
    # data dictionary
    sub_object = data_object['Combined']

    for field in fields_to_extract:
        master_dictionary[test_name][engine_name][field].append(sub_object[field])


def mean(item_list):
    # returns the arithmetic mean of the items in item_list
    return 0 if len(item_list) == 0 else sum(item_list) / len(item_list)


def stdev(item_list):
    # returns the sample standard deviation for the items in item_list
    avg = mean(item_list)
    totaliser = 0
    for item in item_list:
        totaliser += math.pow((item - avg), 2)
    totaliser /= len(item_list)
    return math.sqrt(totaliser)


#####################################################################################
# start of the script.
#
# 1. Process argvs
# 2. Extract data
# 3. Process data
# 4. Display output

# Processing the command line arguments.
normalisation = False
normalisation_engine = ''

if len(sys.argv) > 1:
    args_list = sys.argv[1:]
    counter = 0
    while counter < len(args_list):
        if args_list[counter] == '-n':
            # normalisation
            # the engine to normalise to is the next parameter
            counter += 1
            normalisation = True
            normalisation_engine = args_list[counter]

        counter += 1

print("Analysing results..")
print("No normalisation.." if not normalisation else "Normalising to engine " + normalisation_engine)


# Extracting the data.
fields_to_extract = ['Siege RPS', 'Siege requests']
master_dictionary = analyse_result_set()
for benchmark_name in master_dictionary.keys():
    for engine_name in master_dictionary[benchmark_name].keys():
        for field in fields_to_extract:
            master_dictionary[benchmark_name][engine_name][field] = []

        for i in range(0, master_dictionary[benchmark_name][engine_name]['num_tests'] + 1):
            datum = get_data("results/" + benchmark_name + "/" + engine_name + "-" + str(i) + ".txt")
            if datum is not None:
                extract_data(benchmark_name, engine_name, datum, fields_to_extract, master_dictionary)


# Analysing the data..
for benchmark_name in master_dictionary.keys():
    for engine_name in master_dictionary[benchmark_name].keys():
        for field in fields_to_extract:
            master_dictionary[benchmark_name][engine_name][field + "-mean"] = mean(master_dictionary[benchmark_name][engine_name][field])
            master_dictionary[benchmark_name][engine_name][field + "-stdev"] = stdev(master_dictionary[benchmark_name][engine_name][field])

if normalisation:
    normalised_values = dict()
    for benchmark_name in master_dictionary.keys():
        normalised_values[benchmark_name] = dict()
        for field in fields_to_extract:
            normalised_values[benchmark_name][field + "-mean"] = master_dictionary[benchmark_name][normalisation_engine][field + "-mean"]


# Printing the data
print("\n Output\n********")
for benchmark_name in master_dictionary.keys():
    print("Benchmark " + benchmark_name + ":")
    for engine_name in master_dictionary[benchmark_name].keys():
        print("  " + engine_name + ":")
        for field in fields_to_extract:
            print("    " + field + ":")
            print("      Average             : " + "{0:.3f}".format(master_dictionary[benchmark_name][engine_name][field + "-mean"]))
            print("      Standard Deviation  : " + "{0:.3f}".format(master_dictionary[benchmark_name][engine_name][field + "-stdev"]) + "   (" + "{0:.2f}".format(master_dictionary[benchmark_name][engine_name][field + "-stdev"] / master_dictionary[benchmark_name][engine_name][field + "-mean"] * 100.0) + "%)")

if normalisation:
    print("\nNormalised Output\n****************")
    for benchmark_name in master_dictionary.keys():
        print("Benchmark " + benchmark_name + ":")
        for engine_name in master_dictionary[benchmark_name].keys():
            print("  " + engine_name + ":")
            for field in fields_to_extract:
                print("    " + field + ":")
                print("      Average             : " + "{0:.3f}".format(master_dictionary[benchmark_name][engine_name][field + "-mean"] / float(normalised_values[benchmark_name][field + "-mean"])))
