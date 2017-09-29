#!/usr/bin/env python

import yaml

with open('parameters.yaml') as parmsfile:
  parameters = yaml.load(parmsfile)

for category in parameters.keys():
    print "%s" % category
    print "----"
    cat = parameters[category]
    for variable in cat.keys():
        var = cat[variable]
        if var["datatype"] == "string":
            val = '"%s"' % var["default_value"]
        else:
            val = var["default_value"]
        print "%s =" % variable, val
    print ""
