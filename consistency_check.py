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
"""

import argparse
import yaml