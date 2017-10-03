# TODO:
#       i.  finalize class name and file name
#       ii. comment at top of this file explaining what class should be used for
class yaml_parsing_class(object):
    def __init__(self, yaml_file, grid):
        """
        Class constructor: set up a dictionary of config keywords for when multiple
        default values are provided, and then read the YAML file.
        """
        # 1. Set up dictionary of config keywords as well as a list
        self._config_keyword = dict()
        self._config_keyword['grid'] = grid

        #2. Or maybe we want a list?
        self._provided_keys = []
        self._provided_keys.append("grid = " + self._config_keyword['grid'])

        # 2. Read YAML file
        import yaml
        with open(yaml_file) as parmsfile:
            self._parms = yaml.safe_load(parmsfile)

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
        """
        Returns category names as determined by the 'order :' key in YAML
        """
        # TODO: consistency check!
        #       1. size of get_order should = size of dictionary
        #       2. every key should appear exactly once
        #       3. Something PFT specific if we nest PFT in another dictionary?
        return self._parms["_order"]

    def get_variable_names(self, category_name):
        """
        Returns a sorted list of variables in a specific category.
        For now, variables are sorted alphabetically.
        """
        return sorted(self._parms[category_name].keys(), key=lambda s: s.lower())

    def get_variable_value(self, category_name, variable_name):
        this_var = self._parms[category_name][variable_name]

        # is default value a dictionary? If so, it depends on self._config_keyword
        # Otherwise we're interested in default value
        if isinstance(this_var["default_value"], dict):
            def_value = self._get_correct_default(category_name, variable_name)
        else:
            def_value = this_var["default_value"]

        # call value validation check

        # Append to config keywords if YAML wants it

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

    def _get_correct_default(self, category_name, variable_name):
        """
        This is called when the default_value is a dictionary; it compares
        self._config_keyword to the keys in default_value and returns the
        most appropriate default
        """
        use_key = "default"
        # TODO: Check to make sure default is a key

        for key in self._provided_keys:
            if key in self._parms[category_name][variable_name]["default_value"].keys():
                use_key = key
        return self._parms[category_name][variable_name]["default_value"][use_key]
