#!/usr/bin/env python

################################
# Parse command line arguments #
################################

import argparse

parser = argparse.ArgumentParser(description="Print default MARBL parameter values from YAML file")

# Command line argument to point to YAML file (default is parameters.yaml)
parser.add_argument('--yaml_file', action='store', dest='yaml_file', default='parameters.yaml',
                    help='Location of YAML-formatted MARBL configuration file')

# Command line argument to specify resolution (default is CESM_x1)
parser.add_argument('--res', action='store', dest='resolution', default='CESM_x1',
                    help='Some default values are resolution dependent')

# TODO: Add command line argument for input file
# TODO: maybe add command line argument for path to yaml_parsing_class.py?
#       Then update path before importing the class
args = parser.parse_args()

###################################
# Initialize class from YAML file #
###################################

from yaml_parsing_class import yaml_parsing_class
DefaultParms = yaml_parsing_class(args.yaml_file, args.resolution)

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

    for var_name in sorted(DefaultParms.get_variable_names(cat_name), key=lambda s: s.lower()):
        value = DefaultParms.get_variable_value(cat_name, var_name)
        print "%s =" % var_name, value
