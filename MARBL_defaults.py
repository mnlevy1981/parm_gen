class MARBL_defaults_class(object):
    """ This class contains methods to allow python to interact with the YAML file that
        defines the MARBL parameters and sets default values
    """

    ###############
    # CONSTRUCTOR #
    ###############

    def __init__(self, yaml_file, grid, input_file):
        """ Class constructor: set up a dictionary of config keywords for when multiple
            default values are provided, and then read the YAML file.
        """
        from collections import OrderedDict

        # 1. Set up dictionary of config keywords
        self._config_keyword = OrderedDict()
        self._config_keyword['grid'] = grid

        # 2. Or maybe we want a list?
        self._provided_keys = []
        self._provided_keys.append("grid = " + self._config_keyword['grid'])

        # 3. Read YAML file
        import yaml
        with open(yaml_file) as parmsfile:
            self._parms = yaml.safe_load(parmsfile)

        # 4. Read input file
        #    (Currently not implemented)
        if input_file is not None:
            _abort("ERROR: input_file is not a supported option at this time")

        # 5. Use an ordered dictionary for keeping variable, value pairs
        self.parm_dict = OrderedDict()
        for cat_name in self.get_category_names():
            for var_name in self.get_variable_names(cat_name):
                self._process_variable_value(cat_name, var_name)

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

    ################################################################################

    def get_tracer_cnt(self):
        """ Return the number of tracers MARBL is running with.
            This implementation is a little kludgy, returning the dimsize of tracer_restore_vars
            Computing directly from self._parms['_ecosys_base_tracer_cnt'] would be ideal but it's
            not clear how that would mesh with tracer_restore_vars determining array size.
        """
        restore_vars = self._parms['tracer_dependent']['tracer_restore_vars']
        return _get_dim_size(restore_vars['_array_size'], restore_vars['_array_size_increment'], self.parm_dict)

    ################################################################################

    def get_category_names(self):
        """ Returns category names as determined by the '_order' key in YAML
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
            if key not in ["_order", "_ecosys_base_tracer_cnt"] and key not in self._parms["_order"]:
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

    ################################################################################

    def get_variable_names(self, category_name):
        """ Returns a sorted list of variables in a specific category.
            For now, variables are sorted alphabetically.
        """
        return _sort(self._parms[category_name].keys())

    ################################################################################


    ###################
    # PRIVATE METHODS #
    ###################

    # TODO: define _value_is_valid()
    #       i.  datatype match?
    #       ii. optional valid_value key check

    def _process_variable_value(self, category_name, variable_name):
        """ For a given variable in a given category, add to the self.parm_dict dictionary
            * For derived types and arrays, multiple entries will be added to self.parm_dict

            At this time, the only derived types in the YAML file are also arrays
        """
        this_var = self._parms[category_name][variable_name]
        # Some default values depend on variables from previous categories
        # So we make a local copy of self._provided_keys and append variables as necessary
        local_keys = list(self._provided_keys)
        if category_name == "PFT_counts":
            local_keys.append("PFT_defaults = %s" % self.parm_dict['PFT_defaults'])

        # Is the variable an array? If so, treat each entry separately
        if ("_array_size" in this_var.keys()):
            increment = None
            if "_array_size_increment" in this_var.keys():
                increment = this_var["_array_size_increment"]

            for n, elem_index in enumerate(_get_array_info(this_var["_array_size"], increment, self.parm_dict)):
                # Append "(index)" to variable name
                elem_name = "%s%s" % (variable_name, elem_index)

                # Is this an array of a derived type? If so, treat each element separately
                if isinstance(this_var["datatype"], dict):
                    append_to_keys = (category_name == "PFT_derived_types" and
                                      self.parm_dict['PFT_defaults'].strip('\"') == "CESM2")
                    if append_to_keys:
                        # Add key for specific PFT
                        local_keys.append('%s = "%s"' % (variable_name, self._parms['general_parms']['PFT_defaults']['_CESM2_PFT_keys'][variable_name][n]))
                    for key in _sort(this_var["datatype"].keys()):
                        if key[0] != '_':
                            derived_elem_name = elem_name + "%" + key
                            self.parm_dict[derived_elem_name] = _get_var_value(this_var["datatype"][key], local_keys)
                    if append_to_keys:
                        # Remove PFT-specific key
                        del local_keys[-1]
                else: # Not derived type
                    var_value = _get_var_value(this_var, local_keys)
                    if (isinstance(var_value, list)):
                        self.parm_dict[elem_name] = var_value[n]
                    else:
                        self.parm_dict[elem_name] = var_value
        else: # not an array
            self.parm_dict[variable_name] = _get_var_value(this_var, local_keys)

##########################
# PRIVATE MODULE METHODS #
##########################

################################################################################

def _abort(err_code=0):
    """ This routine imports sys and calls exit
    """
    import sys
    sys.exit(err_code)

################################################################################

def _get_var_value(var_dict, provided_keys):
    """ Return the correct default value for a variable in the MARBL YAML parameter
        file INPUTS:
            * dictionary containing variable information (req: longname, datatype
              and default_value keys)
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

################################################################################

def _sort(a_list, sort_key=lambda s: s.lower()):
    """ Sort a list; default is alphabetical (case-insensitive), but that
        can be overridden with the sort_key argument
    """
    return sorted(a_list, key=sort_key)

################################################################################

def _get_dim_size(dim_in, dim_increment, parm_dict):
    """ If dim_in is an integer, it is the dimension size. Otherwise we need to
        look up the dim_in key in parm_dict.
    """
    # TODO: figure out what to do with tracer count (it's not in the YAML file,
    # but it is needed for tracer_restore_vars)

    if isinstance(dim_in, int):
        dim_out = dim_in
    else:
        dim_out = parm_dict[dim_in]
    if dim_increment is not None:
        for tests in dim_increment.keys():
            checks = tests.split(" = ")
            if parm_dict[checks[0]] == checks[1]:
                dim_out = dim_out + dim_increment[tests]
    return dim_out
################################################################################

def _get_array_info(array_size_in, dim_increment, parm_dict):
    """ Return a list of the proper formatting for array elements, e.g.
            ['(1)', '(2)'] for 1D array or
            ['(1,1)', '(2,1)'] for 2D array
    """

    # List to be returned:
    str_index = []

    # How many dimensions?
    if isinstance(array_size_in, list):
        # Error checking:
        # This script only support 2D arrays for now
        # (and assumes array_size_in is not a list for 1D arrays)
        if len(array_size_in) > 2:
            print "ERROR: _get_array_info() only supports 1D and 2D arrays"
            _abort()

        for i in range(0, _get_dim_size(array_size_in[0], dim_increment, parm_dict)):
            for j in range(0, _get_dim_size(array_size_in[1], dim_increment, parm_dict)):
                str_index.append("(%d,%d)" % (i+1,j+1))
        return str_index

    # How many elements? May be an integer or an entry in self.parm_dict
    for i in range(0, _get_dim_size(array_size_in, dim_increment, parm_dict)):
        str_index.append("(%d)" % (i+1))
    return str_index

################################################################################

