#!/usr/bin/env python

import yaml

with open('parameters.yaml') as parmsfile:
  parameters = yaml.load(parmsfile)

for category in parameters.keys():
    print "%s" % category
    print "----"
    for variable in parameters[category].keys():
        print "%s = " % variable, parameters[category][variable]["default_value"]
    print ""
