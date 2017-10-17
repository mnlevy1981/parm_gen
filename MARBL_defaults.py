class MARBL_defaults_class(object):
    """ This class contains methods to allow python to interact with the YAML file that
        defines the MARBL parameters and sets default values.

        This file also contains several subroutines that are not part of the class but are
        called by member functions in the class.
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
        self._input_dict = _parse_input_file(input_file)

        # 5. Use an ordered dictionary for keeping variable, value pairs
        self.parm_dict = OrderedDict()
        for cat_name in self.get_category_names():
            for var_name in self.get_variable_names(cat_name):
                self._process_variable_value(cat_name, var_name)

        if (self._input_dict):
            print "ERROR: Did not fully parse input file:"
            for varname in self._input_dict.keys():
                print "Could not handle variable %s" % varname
            _abort()

    ################################################################################
    #                             PUBLIC CLASS METHODS                             #
    ################################################################################

    def get_tracer_cnt(self):
        """ Return the number of tracers MARBL is running with.
        """

        return (self._parms['_tracer_cnt']['default'] +
                _add_increments(self._parms['_tracer_cnt']['increments'], self.parm_dict))

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
            if key not in ["_order", "_tracer_cnt"] and key not in self._parms["_order"]:
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

    def get_subcategory_names(self):
        """ Returns a sorted list of subcategories in a specific category.
            For now, the list is sorted naturally (so 10 appears after 9, not after 1).

            Optional: only return variables in a specific subcategory
        """
        subcat_list = []
        for cat_name in self._parms['_order']:
            for var_name in _sort(self._parms[cat_name].keys()):
                this_subcat = self._parms[cat_name][var_name]['subcategory']
                if this_subcat not in subcat_list:
                    subcat_list.append(this_subcat)
        return _sort(subcat_list, sort_key=_natural_sort_key)

    ################################################################################

    def get_variable_names(self, category_name):
        """ Returns a sorted list of variables in a specific category.
            For now, the list is sorted alphabetically.
        """
        return _sort(self._parms[category_name].keys())

    ################################################################################

    def get_parm_dict_variable_names(self, subcategory):
        """ Returns a sorted list of variables in a specific category
            and subcategory, expanding variable names if they are arrays
            or derived types
        """
        varlist = []
        for cat_name in self._parms['_order']:
            for var_name in _sort(self._parms[cat_name].keys()):
                this_var = self._parms[cat_name][var_name]
                if this_var['subcategory'] == subcategory:
                    for parm_key in this_var['_list_of_parm_names']:
                        varlist.append(parm_key)
        return _sort(varlist, sort_key=_natural_sort_key)

    ################################################################################
    #                            PRIVATE CLASS METHODS                             #
    ################################################################################

    # TODO: define _value_is_valid()
    #       i.  datatype match?
    #       ii. optional valid_value key check

    def _process_variable_value(self, category_name, variable_name):
        """ For a given variable in a given category, add to the self.parm_dict dictionary
            * For derived types and arrays, multiple entries will be added to self.parm_dict

            Also introduce a new key to the variable dictionary, '_list_of_parm_names', that
            is populated with a list of all the keys added to self.parm_dict for this variable
            (just varname for scalars, but multiple keys for arrays and derived types)

            NOTE: At this time, the only derived types in the YAML file are also arrays
        """
        this_var = self._parms[category_name][variable_name]
        this_var['_list_of_parm_names'] = []
        # Some default values depend on variables from previous categories
        # So we make a local copy of self._provided_keys and append variables as necessary
        local_keys = list(self._provided_keys)
        if category_name == "PFT_counts":
            local_keys.append("PFT_defaults = %s" % self.parm_dict['PFT_defaults'])

        # Is the variable an array? If so, treat each entry separately
        if ("_array_size" in this_var.keys()):

            for n, elem_index in enumerate(_get_array_info(this_var["_array_size"], self.parm_dict)):
                # Append "(index)" to variable name
                elem_name = "%s%s" % (variable_name, elem_index)

                # Is this an array of a derived type? If so, treat each element separately
                if isinstance(this_var["datatype"], dict):
                    append_to_keys = (category_name == "PFT_derived_types" and
                                      self.parm_dict['PFT_defaults'].strip('\"') == "CESM2")
                    if append_to_keys:
                        # Add key for specific PFT
                        local_keys.append('%s = "%s"' % (variable_name, self._parms['general_parms']['PFT_defaults']['_CESM2_PFT_keys'][variable_name][n]))

                    for key in _sort_with_specific_suffix_first(this_var["datatype"].keys(),'_cnt'):
                        this_component = this_var["datatype"][key]
                        if key[0] != '_':
                            derived_elem_name = elem_name + "%" + key
                            # Is this key an array or a scalar?
                            if ("_array_size" in this_component.keys()):
                                try:
                                    array_len = elem_name+"%"+this_component["_array_len_to_print"]
                                except:
                                    array_len = this_component["_array_size"]
                                for m, elem_index2 in enumerate(_get_array_info(array_len, self.parm_dict)):
                                    derived_elem_name2 = derived_elem_name + "(%d)" % (m+1)
                                    var_value = _get_var_value(derived_elem_name2, this_component, local_keys, self._input_dict)
                                    if isinstance(var_value, list):
                                        self.parm_dict[derived_elem_name2] = var_value[n]
                                    else:
                                        self.parm_dict[derived_elem_name2] = var_value
                                    this_var['_list_of_parm_names'].append(derived_elem_name2)
                            else:
                                self.parm_dict[derived_elem_name] = _get_var_value(derived_elem_name, this_component, local_keys, self._input_dict)
                                this_var['_list_of_parm_names'].append(derived_elem_name)
                    if append_to_keys:
                        # Remove PFT-specific key
                        del local_keys[-1]
                else: # Not derived type
                    var_value = _get_var_value(elem_name, this_var, local_keys, self._input_dict)
                    if (isinstance(var_value, list)):
                        self.parm_dict[elem_name] = var_value[n]
                    else:
                        self.parm_dict[elem_name] = var_value
                    this_var['_list_of_parm_names'].append(elem_name)
        else: # not an array
            self.parm_dict[variable_name] = _get_var_value(variable_name, this_var, local_keys, self._input_dict)
            this_var['_list_of_parm_names'].append(variable_name)

################################################################################
#                            PRIVATE MODULE METHODS                            #
################################################################################

def _abort(err_code=0):
    """ This routine imports sys and calls exit
    """
    import sys
    sys.exit(err_code)

################################################################################

def _get_var_value(varname, var_dict, provided_keys, input_dict):
    """ Return the correct default value for a variable in the MARBL YAML parameter
        file INPUTS:
            * dictionary containing variable information (req: longname, datatype
              and default_value keys)
            * list of keys to try to match in default_value
            * dictionary containing values from input file
    """
    # Either get value from input file or from the YAML
    if varname in input_dict.keys():
        # Ignore ' and " from strings
        def_value = input_dict[varname].strip('"').strip("'")
        # Remove from input file dictionary; if dictionary is not empty after processing
        # all input file lines, then it included a bad variable in it
        del input_dict[varname]
    # Note that if variable foo is an array, then foo = bar in the input file
    # should be treated as foo(1) = bar
    elif varname[-3:] == "(1)" and varname[:-3] in input_dict.keys():
        def_value = input_dict[varname[:-3]].strip('"').strip("'")
        # Remove from input file dictionary; if dictionary is not empty after processing
        # all input file lines, then it included a bad variable in it
        del input_dict[varname[:-3]]
    else:
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
    if var_dict["datatype"] == "real" and isinstance(def_value, str):
        return "%20.15e" % eval(def_value)
    if var_dict["datatype"] == "integer" and isinstance(def_value, str):
        return int(def_value)
    return def_value

################################################################################

def _sort(list_in, sort_key=None):
    """ Sort a list; default is alphabetical (case-insensitive), but that
        can be overridden with the sort_key argument
    """
    if sort_key is None:
        sort_key = lambda s: s.lower()
    return sorted(list_in, key=sort_key)

################################################################################

def _sort_with_specific_suffix_first(list_in, suffix=None, sort_key=None):
    """ Sort, but make sure entries that end in a specified suffix are listed first
    """

    # 1. initialize empty list
    list_out = []

    # 2. Anything that ends in suffix gets appended to list_out first
    if suffix is not None:
        for list_entry in _sort(list_in, sort_key):
            if list_entry.endswith(suffix):
                list_out.append(list_entry)

    # 3. Sort everything else
    for list_entry in _sort(list_in, sort_key):
        if list_entry not in list_out:
            list_out.append(list_entry)
    return list_out

################################################################################

def _natural_sort_key(string_):
    """ From https://stackoverflow.com/questions/2545532/python-analog-of-natsort-function-sort-a-list-using-a-natural-order-algorithm/3033342#3033342
    """
    import re
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

################################################################################

def _add_increments(increments, parm_dict):
    """ Some values need to be adjusted depending on values in parm_dict
    """
    change = 0
    for key_check in increments.keys():
        checklist = key_check.split(" = ")
        if parm_dict[checklist[0]] == checklist[1]:
            change = change + increments[key_check]
    return change

################################################################################

def _get_dim_size(dim_in, parm_dict):
    """ If dim_in is an integer, it is the dimension size. Otherwise we need to
        look up the dim_in key in parm_dict.
    """

    if isinstance(dim_in, dict):
        dim_start = dim_in['default']
        check_increment = ('increments' in dim_in.keys())
    else:
        dim_start = dim_in
        check_increment = False

    if isinstance(dim_start, int):
        dim_out = dim_start
    else:
        dim_out = parm_dict[dim_start]

    if check_increment:
        dim_out = dim_out + _add_increments(dim_in['increments'], parm_dict)

    return dim_out
################################################################################

def _get_array_info(array_size_in, parm_dict):
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

        for i in range(0, _get_dim_size(array_size_in[0], parm_dict)):
            for j in range(0, _get_dim_size(array_size_in[1], parm_dict)):
                str_index.append("(%d,%d)" % (i+1,j+1))
        return str_index

    # How many elements? May be an integer or an entry in self.parm_dict
    for i in range(0, _get_dim_size(array_size_in, parm_dict)):
        str_index.append("(%d)" % (i+1))
    return str_index

################################################################################

def _string_to_substring(str_in, separator):
    """ Basically the python native split() function, but ignore separator that
        is inside quotes. So (using separator = ',')
            'abc, def, gh' -> ['abc', 'def', 'gh']
        but
            'abc,"def, gh"' -> ['abc', '"def, gh"']
            "abc,'def, gh'" -> ['abc', '"def, gh"']

        Note: unexpected results if str_in is missing a closing ' or "
    """

    import re
    re_separator = separator+"(?=(?:[^\"\']|[\"|\'][^\"\']*[\"|\'])*$)"
    return re.split(re_separator, str_in)

################################################################################

def _parse_input_file(input_file):
    """ 1. Read an input file; ignore blank lines and non-quoted Fortran comments.
        2. Turn lines of the form
              variable = value
           Into input_dict['variable'] = value
        3. Return input_dict
    """
    input_dict = dict()
    try:
        f = open(input_file, "r")
        for line in f:
            # Ignore comments in input file!
            line_loc = _string_to_substring(line, '!')[0]

            # ignore empty lines
            if len(line_loc.lstrip()) == 0:
                continue

            line_list = line_loc.strip().split('=')
            var_name = line_list[0].strip()
            value = line_list[1].strip()
            val_array = _string_to_substring(value, ',')
            if len(val_array) > 1:
                # Treat comma-delimited value as an array
                for n, value in enumerate(val_array):
                    suffix = "(%d)" % (n+1)
                    input_dict[var_name+suffix] = value.strip()
            else:
                # Single value
                input_dict[var_name] = value
        f.close()
    except TypeError:
        # If inputfile == None then the open will result in TypeError
        pass
    except:
        _abort("ERROR: input_file '%s' was not found" % input_file)
    return input_dict

################################################################################
