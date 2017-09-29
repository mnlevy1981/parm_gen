#!/usr/bin/env python

import yaml

with open('parameters.yaml') as parmsfile:
  parameters = yaml.safe_load(parmsfile)

# Validation
# ---------
# 1. Is variable from input file defined in dictionary?
# 2. Is the value provided valid?
#    i. datatype match?
#    ii. YAML could have is_valid() function!
#
# NOTE: need to do something about parsing marbl_in
# (could be here or in the "for var_name" loop)

for cat_name in parameters.keys():
    print "! %s" % cat_name
    print "! ----"
    category = parameters[cat_name]
    for var_name in sorted(category.keys(), key=lambda s: s.lower()):
        variable = category[var_name]
        if variable["datatype"] == "string":
            val = '"%s"' % variable["default_value"]
        else:
            val = variable["default_value"]
        print "%s =" % var_name, val
    print ""

