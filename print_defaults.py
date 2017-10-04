#!/usr/bin/env python

################################
# Parse command line arguments #
################################

import argparse

parser = argparse.ArgumentParser(description="Print default MARBL parameter values from YAML file")

# Command line argument to point to YAML file (default is parameters.yaml)
parser.add_argument('-y', '--yaml_file', action='store', dest='yaml_file', default='parameters.yaml',
                    help='Location of YAML-formatted MARBL configuration file')

# Command line argument to specify resolution (default is CESM_x1)
parser.add_argument('-g', '--grid', action='store', dest='grid', default='CESM_x1',
                    help='Some default values are grid-dependent')

# Command line argument to specify an input file which would override the YAML
parser.add_argument('-i', '--input_file', action='store', dest='input_file', default=None,
                    help='A file that overrides values in YAML')

# Path to directory containing MARBL_defaults.py
parser.add_argument('-l', '--lib_dir', action='store', dest='lib_dir', default='./',
                    help='Directory that contains MARBL_defaults.py')
args = parser.parse_args()

###################################
# Initialize class from YAML file #
###################################

from sys import path
path.insert(0, args.lib_dir)
from MARBL_defaults import MARBL_defaults_class
DefaultParms = MARBL_defaults_class(args.yaml_file, args.grid, args.input_file)

################
# BEGIN SCRIPT #
################

first_cat = True
for cat_name in DefaultParms.get_category_names():
    if first_cat:
        first_cat = False
    else:
        print ""

    bars = "-" * len(cat_name)
    print "! %s" % bars
    print "! %s" % cat_name
    print "! %s" % bars
    print ""

    for var_name in DefaultParms.get_variable_names(cat_name):
        value = DefaultParms.get_variable_value(cat_name, var_name)
        print "%s =" % var_name, value
