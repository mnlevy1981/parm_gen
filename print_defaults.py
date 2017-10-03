#!/usr/bin/env python

################################
# Parse command line arguments #
################################

import argparse

parser = argparse.ArgumentParser(description="Print default MARBL parameter values from YAML file")

parser.add_argument('--res', action='store', dest='resolution',
                    help='Some default values are resolution dependent')

# TODO: Other potential arguments
#       1. Full path for YAML file? (default: ./parameters.yaml)

args = parser.parse_args()
key = args.resolution

###################################
# Initialize class from YAML file #
###################################

from yaml_parsing_class import yaml_parsing_class
DefaultParms = yaml_parsing_class('parameters.yaml', args.resolution)

################
# BEGIN SCRIPT #
################

# Validation
# ---------
# 1. Is variable from input file defined in dictionary?
# 2. Is the value provided valid?
#    i. datatype match?
#    ii. YAML could have is_valid() function!
#
# NOTE: need to do something about parsing marbl_in
# (could be here or in the "for var_name" loop)

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
