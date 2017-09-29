#!/usr/bin/env python

# This script reads in

import yaml

# Read YAML file to get variables / values
with open('parameters.yaml') as parmsfile:
  parameters = yaml.load(parmsfile)

in_file  = "marbl_settings_mod.template"
out_file = "marbl_settings_mod.F90"

# Fortran declarations are a dictionary based on datatype in YAML
types = dict()
types["string"] = "character(len=char)"
types["logical"] = "logical(log_kind)"
types["integer"] = "integer(int_kind)"
types["real"] = "real(r8)"


# Read template file line by line
with open(in_file) as fin:
    lines = [x.strip('\n') for x in fin.readlines()]

with open(out_file, 'w') as fout:
    for single_line in lines:
        # 1. ignore !!!
        if single_line.lstrip().startswith('!!!'):
            continue

        # 2. replace !## with auto-generated code
        if single_line.lstrip().startswith('!##'):
            # i. Make sure we keep the leading spaces
            leading_spaces = " " * (len(single_line) - len(single_line.lstrip()))

            # ii. split single_line into an action and a category
            line_array = single_line.split()
            # line_array[0] is "!##"
            action = line_array[1]
            cat_name = line_array[2]

            # iii. act based on action
            if action == "declare":
                for var_name in parameters[cat_name]:
                    fout.write("%s%s, target :: %s   ! %s\n" % (leading_spaces,
                                                                types[parameters[cat_name][var_name]["datatype"]],
                                                                var_name,
                                                                parameters[cat_name][var_name]["longname"]))
            if action == "default":
                for var_name in parameters[cat_name]:
                    if parameters[cat_name][var_name]["datatype"] == "string":
                        fout.write("%s%s = '%s'\n" % (leading_spaces,
                                                    var_name,
                                                    parameters[cat_name][var_name]["default_value"]))
                    if parameters[cat_name][var_name]["datatype"] == "integer":
                        fout.write("%s%s = %d\n" % (leading_spaces,
                                                    var_name,
                                                    parameters[cat_name][var_name]["default_value"]))
                    if parameters[cat_name][var_name]["datatype"] == "logical":
                        strval = ".true." if parameters[cat_name][var_name]["default_value"] else ".false."
                        fout.write("%s%s = %s\n" % (leading_spaces,
                                                    var_name,
                                                    strval))
            continue

        # 3. copy all other lines
        fout.write("%s\n" % single_line)
