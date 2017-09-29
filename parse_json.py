#!/usr/bin/env python

import json

with open('parameters.json') as parmsfile:
  parameters = json.load(parmsfile)

for category in parameters.keys():
    print "%s" % category
    print "----"
    for variable in parameters[category].keys():
        print "%s = " % variable, parameters[category][variable]["default_value"]
    print ""