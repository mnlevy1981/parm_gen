# TODO:
#       i.  finalize class name and file name
#       ii. comment at top of this file explaining what class should be used for
class yaml_parsing_class(object):
    def __init__(self, yaml_file, key=None):
        import yaml
        with open(yaml_file) as parmsfile:
            self._parms = yaml.safe_load(parmsfile)
        # TODO: would like self._key to be a dictionary ({'res' : ..., 'var_PtoC' : ..., others?})
        self._key   = key

##################
# PUBLIC METHODS #
##################

# TODO:
#       1. PFT defaults (separate YAML file?)
#       2. Parse an input file
#          i.   figure  out workflow (read YAML then over-write?)
#          ii.  things like PFT array sizes will be tricky!
#          iii. Thought: two dictionarys, self._parms (renamed self._yaml_parms) and self._input_parms
#                        Look in _input_parms first, if no key match then fallback to YAML?
#                        Or maybe combine YAML and inputfile during __init__?
    def get_category_names(self):
        return self._parms.keys()

    def get_variable_names(self, category_name):
        return self._parms[category_name].keys()

    def get_variable_value(self, category_name, variable_name):
        this_var = self._parms[category_name][variable_name]

        # is default value a dictionary? If so, it depends on self._key
        # Otherwise we're interested in default value
        if isinstance(this_var["default_value"], dict):
            def_value = self._match_key(category_name, variable_name)
        else:
            def_value = this_var["default_value"]

        # if variable is a string, put quotes around the default value
        if this_var["datatype"] == "string":
            return '"%s"' % def_value
        return def_value

###################
# PRIVATE METHODS #
###################

# TODO: define _value_is_valid()
#       i.  datatype match?
#       ii. optional valid_value key check

    def _match_key(self, category_name, variable_name):
        key = self._key
        if key not in self._parms[category_name][variable_name]["default_value"].keys():
            key = "default"
        return self._parms[category_name][variable_name]["default_value"][key]
