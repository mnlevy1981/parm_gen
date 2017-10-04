class MARBL_defaults_class(object):
    """
    This class contains methods to allow python to interact with the YAML file that
    defines the MARBL parameters and sets default values
    """

###############
# CONSTRUCTOR #
###############

    def __init__(self, yaml_file, grid, input_file):
        """
        Class constructor: set up a dictionary of config keywords for when multiple
        default values are provided, and then read the YAML file.
        """
        # 1. Set up dictionary of config keywords as well as a list
        self._config_keyword = dict()
        self._config_keyword['grid'] = grid

        # 2. Or maybe we want a list?
        self._provided_keys = []
        self._provided_keys.append("grid = " + self._config_keyword['grid'])

        # 3. Empty dictionary for keeping variable, value pairs
        self.parm_dict = dict()

        # 4. Or maybe a list will be easier to keep in proper order?
        self.parm_varname = []
        self.parm_value = []

        # 5. Read YAML file
        import yaml
        with open(yaml_file) as parmsfile:
            self._parms = yaml.safe_load(parmsfile)

        # 6. Read input file
        #    (Currently not implemented)
        if input_file is not None:
            _abort("ERROR: input_file is not a supported option at this time")
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
        Returns category names as determined by the '_order' key in YAML
        """

        # Consistency checks:
        # 1. All keys listed in self._parms["_order"] should also be in self._parms.keys()
        for key in self._parms["_order"]:
            if key not in self._parms.keys():
                msg = "ERROR: can not find '" + key + "' in YAML file"
                _abort(msg)

        # 2. All keys listed in self._parms.keys() should also be in self._parms["_order"]
        #    (except _order itself)
        for key in self._parms.keys():
            if key not in ["_order"] and key not in self._parms["_order"]:
                msg = "ERROR: '" + key + "' is not listed in '_order' and won't be processed"
                _abort(msg)

        # 3. No duplicates in _order
        unique_keys = []
        for key in self._parms["_order"]:
            if key in unique_keys:
                msg = "ERROR: '" + key + "' appears in '_order' multiple times"
                _abort(msg)
            unique_keys.append(key)

        return self._parms["_order"]

    def get_variable_names(self, category_name):
        """
        Returns a sorted list of variables in a specific category.
        For now, variables are sorted alphabetically.
        """
        return sorted(self._parms[category_name].keys(), key=lambda s: s.lower())

    def process_variable_value(self, category_name, variable_name):
        this_var = self._parms[category_name][variable_name]

        # Is the variable datatype a dictionary? If so, it is a derived type
        # and needs to be handled differently
        if isinstance(this_var["datatype"], dict):
            return
        self.parm_dict[variable_name] = _get_var_value(this_var, self._provided_keys)
        self.parm_varname.append(variable_name)
        self.parm_value.append(self.parm_dict[variable_name])


###################
# PRIVATE METHODS #
###################

# TODO: define _value_is_valid()
#       i.  datatype match?
#       ii. optional valid_value key check

##########################
# PRIVATE MODULE METHODS #
##########################

def _abort(err_code=0):
    """
    This routine imports sys and calls exit
    """
    import sys
    sys.exit(err_code)

def _get_var_value(var_dict, provided_keys):
    """
    Return the correct default value for a variable in the MARBL YAML parameter file
    INPUTS:
        * dictionary containing variable information (req: longname, datatype and default_value keys)
        * list of keys to try to match in default_value
    """
    # is default value a dictionary? If so, it depends on self._config_keyword
    # Otherwise we're interested in default value
    if isinstance(var_dict["default_value"], dict):
        # default must be a key in the default_value dictionary!
        if "default" not in var_dict["default_value"].keys():
            msg = "ERROR: " + var_dict["longname"] + " does not have a default key in default_value"
            _abort(msg)

        # return "default" entry in default_values dictionary unless one of the provided keys matches
        use_key = "default"
        for key in provided_keys:
            if key in var_dict["default_value"].keys():
                use_key = key
        def_value = var_dict["default_value"][use_key]
    else:
        def_value = var_dict["default_value"]

    # call value validation check

    # Append to config keywords if YAML wants it

    # if variable is a string, put quotes around the default value
    if var_dict["datatype"] == "string":
        return '"%s"' % def_value
    return def_value
