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

##################################
# Read YAML file into dictionary #
##################################

import yaml

with open('parameters.yaml') as parmsfile:
  parameters = yaml.safe_load(parmsfile)

##################################################################
# Return correct default value if multiple defaults are provided #
##################################################################

def match_key(key, dictionary):
    # TODO:
    #       1. Move to a separate library (maybe define a class?)
    #          So this can be used by gen_code.py as well
    #       2. Handle multiple provided keys (recursive, nested?)
    if key not in dictionary.keys():
        key = 'default'
    return dictionary[key]

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
for cat_name in parameters.keys():
    if first_cat:
        first_cat = False
    else:
        print ""

    bars = "-" * len(cat_name)
    print "! %s" % bars
    print "! %s" % cat_name
    print "! %s" % bars
    print ""

    category = parameters[cat_name]
    for var_name in sorted(category.keys(), key=lambda s: s.lower()):
        variable = category[var_name]
        if isinstance(variable["default_value"], dict):
            value = match_key(key, variable["default_value"])
        else:
            if variable["datatype"] == "string":
                value = '"%s"' % variable["default_value"]
            else:
                value = variable["default_value"]
        print "%s =" % var_name, value
