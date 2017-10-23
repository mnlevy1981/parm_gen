#!/usr/bin/env python
"""

$ consistency_check.py -y YAML_FILE
YAML_FILE -- MARBL configuration file (in YAML format)

    Read a YAML file, make sure it conforms to MARBL config file standards
    1. _order is a top-level key
    2. Everything listed in _order is a top-level key
    3. All top-level keys that do not begin with '_' are listed in _order
    4. All second-level dictionaries (variable names) contain datatype key
    5. If datatype is not a dictionary, variable dictionary keys also included
       longname, subcategory, units, default_value
    6. If datatype is a dictionary, all keys in the datatype are variables per (5)
    7. In a variable (or datatype entry) where default_value is a dictionary,
       "default" is a key
    NOTE: (7) is checked explicitly along with (5) and (6) in valid_variable_dict()
"""

#### ABORT SUBROUTINE ####

def abort(exit_code=0):
    import sys
    sys.exit(exit_code)

#### VARIABLE DICTIONARY CHECK ####

def valid_variable_dict(var_dict):
    """ Return False if dictionary does not contain any of the following:
        * longname
        * subcategory
        * units
        * datatype
        * default_value
    """

    for key_check in ["longname", "subcategory", "units", "datatype", "default_value"]:
        if key_check not in var_dict.keys():
            return False
    if isinstance(var_dict["default_value"], dict):
        # Make sure "default" is a valid key if default_value is a dictionary
        return "default" in var_dict["default_value"].keys()
    return True

#### MAIN PROGRAM ####
import argparse
try:
    import yaml
except:
    abort("ERROR: Can not find PyYAML library")

parser = argparse.ArgumentParser(description="Print default MARBL parameter values from YAML file")

# Command line argument to point to YAML file (default is parameters.yaml)
parser.add_argument('-y', '--yaml_file', action='store', dest='yaml_file', default='parameters.yaml',
                    help='Location of YAML-formatted MARBL configuration file')

args = parser.parse_args()

with open(args.yaml_file) as parmsfile:
    YAMLdict = yaml.safe_load(parmsfile)

# 1. _order is a top-level key
if "_order" not in YAMLdict.keys():
    abort("ERROR: Can not find _order key")

# 2. Everything listed in _order is a top-level key
for cat_name in YAMLdict["_order"]:
    if cat_name not in YAMLdict.keys():
        abort("ERROR: Can not find %s category" % cat_name)

for cat_name in YAMLdict.keys():
    if cat_name[0] != '_':
    # 3. All top-level keys that do not begin with '_' are listed in _order
        if cat_name not in YAMLdict["_order"]:
            abort("ERROR: %s not included in _order" % cat_name)

        # 4. All second-level dictionaries (variable names) contain datatype key
        for var_name in YAMLdict[cat_name].keys():
            if "datatype" not in YAMLdict[cat_name][var_name].keys():
                abort("ERROR: variable %s does not contain a key for datatype")

            if not isinstance(YAMLdict[cat_name][var_name]["datatype"], dict):
                # 5. If datatype is not a dictionary, variable dictionary keys should include
                #    longname, subcategory, units, datatype, default_value
                #    Also, if default_value is a dictionary, that dictionary needs to contain "default" key
                if not valid_variable_dict(YAMLdict[cat_name][var_name]):
                    abort("ERROR: %s is not a well-defined variable in YAML" % var_name)
            else:
                # 6. If datatype is a dictionary, all keys in the datatype are variables per (5)
                for subvar_name in YAMLdict[cat_name][var_name]["datatype"].keys():
                    if subvar_name[0] != '_':
                        if not valid_variable_dict(YAMLdict[cat_name][var_name]["datatype"][subvar_name]):
                            abort("ERROR: %s%%%s is not a well-defined variable in YAML" % (var_name, subvar_name))



