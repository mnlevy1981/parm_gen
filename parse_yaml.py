#!/usr/bin/env python

import yaml

with open('parameters.yaml') as parmsfile:
  parameters = yaml.load(parmsfile)

for cat_name in parameters.keys():
    print "%s" % cat_name
    print "----"
    category = parameters[cat_name]
    for var_name in category.keys():
        variable = category[var_name]
        if variable["datatype"] == "string":
            val = '"%s"' % variable["default_value"]
        else:
            val = variable["default_value"]
        print "%s =" % var_name, val
    print ""
