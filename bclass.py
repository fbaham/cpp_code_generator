#!/usr/bin/env python
#=======================================================================
# Copyright (C) 2013 William Hallahan
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#=======================================================================

import time
from type_info import TypeInfo
from type_and_name_info import TypeAndNameInfo
from function_info import FunctionInfo
from bparse import Bparse

def get_date_and_year():
    now = time.ctime()
    now_list = now.split()
    time_list = now_list[3].split(':')
    day_of_week = now_list[0]
    month = now_list[1]
    day_number = now_list[2]
    year = now_list[4]
    date = '{0} {1}, {2}'.format(month, day_number, year)
    return date, year

def create_cpp_class_files(input_file_name,
                           class_name,
                           base_class,
                           author,
                           full_header,
                           abstract_class):
    """ Create class files. """
    # Generate all of the class name strings.
    if not author:
        author = 'William Hallahan'
    class_definition_file_name = '{0}.h'.format(class_name)
    class_implementation_file_name = '{0}.cpp'.format(class_name)
    conditional_include_name_text = '{0}_H'.format(class_name)
    conditional_include_name_text = conditional_include_name_text.upper()
    # Open the input file.
    with open(input_file_name, 'r') as input_file:
        # Create a parser.
        parser = Bparse(input_file)
        # Parse the input file.
        data_member_type_and_name_info_list = []
        definition_class_name_set = set()
        implementation_class_name_set = set()
        function_info_list = []
        parse_success_status = True
        exception_line_number = 0
        try:
            parser.parse(data_member_type_and_name_info_list,
                         definition_class_name_set,
                         implementation_class_name_set,
                         function_info_list,
                         class_name)
        except Exception as err:
            # Something bad happened in the parser.  Attach the input file line number to
            # The exception information.
            err.args = ['{0}\nError parsing input file at line {1}.'.format(err.args[0], parser.get_line_number())]
            raise
        # If the class is derived from a base class, then include
        # the header file for the base class.
        if base_class:
            base_class_type_info = TypeInfo()
            base_class_type_info.set_name(base_class)
            parser.save_include_name(definition_class_name_set,
                                     implementation_class_name_set,
                                     base_class_type_info)
        # If a pure abstract class then ensure that all virtual method
        # declarations end with '= 0'
        if abstract_class:
            for function_info in function_info_list:
                # Only make 'virtual' methods be abstract.
                method_type_and_name_info = function_info.get_method_type_and_name_info()
                method_type_info = method_type_and_name_info.get_type_info()
                # Test for a virtual method.  Do not make a virtual destructor be abstract
                # unless the user already specified '= 0' at the end in the input file.
                if (method_type_info.get_static_virtual_qualifier_type() == TypeInfo.VIRTUAL_QUALIFIER_TYPE
                    and function_info.get_method_type() != FunctionInfo.METHOD_DESTRUCTOR):
                    qualifier_text = function_info.get_qualifier()
                    if not '=' in qualifier_text:
                        qualifier_text = '{0} = 0'.format(qualifier_text)
                        function_info.set_qualifier(qualifier_text)
                    # Do not implement abstract functions.
                    function_info.set_write_the_implementation(False)
        # If there is a single virtual method then set the destructor to be virtual.
        # Check for any virtual method.  Treat the destructor as a regular method.
        has_virtual_method = False
        for function_info in function_info_list:
            method_type_and_name_info = function_info.get_method_type_and_name_info()
            method_type_info = method_type_and_name_info.get_type_info()
            if method_type_info.get_static_virtual_qualifier_type() == TypeInfo.VIRTUAL_QUALIFIER_TYPE:
                has_virtual_method = True
                break
        if has_virtual_method:
            for function_info in function_info_list:
                if function_info.get_method_type() == FunctionInfo.METHOD_DESTRUCTOR:
                    method_type_and_name_info = function_info.get_method_type_and_name_info()
                    method_type_info = method_type_and_name_info.get_type_info()
                    method_type_info.set_static_virtual_qualifier_type(TypeInfo.VIRTUAL_QUALIFIER_TYPE)
        #--------------------------------------------------------------
        # Write the class definition file.
        #--------------------------------------------------------------
        # Open the class definition file.
        with open(class_definition_file_name, 'w') as class_definition_file:
            # Write the class definition file header.
            date_text, year_text = get_date_and_year()
            stars_text = '//**********************************************************************'
            class_definition_file.write('{0}\n'.format(stars_text))
            class_definition_file.write('// Class Definition File: {0}\n'.format(class_definition_file_name))
            class_definition_file.write('// Author: {0}\n'.format(author))
            class_definition_file.write('// Date: {0}\n'.format(date_text))
            class_definition_file.write('//\n')
            class_definition_file.write('// Abstract:\n')
            class_definition_file.write('//\n')
            class_definition_file.write('//   This file contains the class definition for class {0}.\n'.format(class_name))
            class_definition_file.write('//\n')
            class_definition_file.write('// Copyright (c) {0}, {1}.\n'.format(year_text, author))
            class_definition_file.write('//\n')
            class_definition_file.write('{0}\n'.format(stars_text))
            class_definition_file.write('\n')
            class_definition_file.write('#ifndef {0}\n'.format(conditional_include_name_text))
            class_definition_file.write('#define {0}\n'.format(conditional_include_name_text))
            # Write the class definition include statements.
            # Write the bracketed include statements first.
            include_name = ''
            if len(definition_class_name_set) > 0:
                class_definition_file.write('\n')
                # Write the include files lines for file names that are bracketed, such as '#include <vector>'.
                for include_name in definition_class_name_set:
                    if include_name[0] == '<':
                        class_definition_file.write('#include {0};\n'.format(include_name))
                # Write the include files lines for ordinary file names, such as '#include 'Foo.h''.
                for include_name in definition_class_name_set:
                    if include_name[0] != '<':
                        if '.h' not in include_name:
                            include_name = '{0}.h'.format(include_name)
                        class_definition_file.write('#include "{0}";\n'.format(include_name))
            # Write forward declarations.
            if len(implementation_class_name_set)  > 0:
                class_definition_file.write('\n')
                for implementation_class_name in implementation_class_name_set:
                    class_definition_file.write('class {0};\n'.format(implementation_class_name))
            # Write the class definition header.
            function_header_separator_text = '//======================================================================'
            class_definition_file.write('\n{0}\n'.format(function_header_separator_text))
            if abstract_class:
                class_definition_file.write('// Abstract class Definition')
            else:
                class_definition_file.write('// Class Definition\n')
            class_definition_file.write('{0}\n\n'.format(function_header_separator_text))
            # Start the class definition.
            if base_class:
                class_definition_file.write('class {0} : public {1}\n{2}\n'.format(class_name, base_class, '{'))
            else:
                class_definition_file.write('class {0}\n{1}\n'.format(class_name, '{'))
            # Write the class definition data member declarations.
            # Skip the static data members in this loop and write
            # the static declarations afterward.
            if not abstract_class:
                class_definition_file.write('protected:\n\n')
                for data_member_type_and_name in data_member_type_and_name_info_list:
                    the_type_info = data_member_type_and_name.get_type_info()
                    if the_type_info.get_static_virtual_qualifier_type() != TypeInfo.STATIC_QUALIFIER_TYPE:
                        render_text = data_member_type_and_name.get_type_and_name_text(TypeInfo.RENDER_DEFINITION_DATA_TYPE,
                                                                                       TypeAndNameInfo.RENDER_NO_VALUE)
                        class_definition_file.write('    {0};\n'.format(render_text))
                class_definition_file.write('\n')
                # Write the static data members.
                for data_member_type_and_name in data_member_type_and_name_info_list:
                    the_type_info = data_member_type_and_name.get_type_info()
                    if the_type_info.get_static_virtual_qualifier_type() == TypeInfo.STATIC_QUALIFIER_TYPE:
                        render_text = data_member_type_and_name.get_type_and_name_text(TypeInfo.RENDER_DEFINITION_DATA_TYPE,
                                                                                       TypeAndNameInfo.RENDER_NO_VALUE)
                        class_definition_file.write('    {0};\n'.format(render_text))
            # Write the class definition functions declarations
            # For the 'no copy' copy constructor and operator=().
            # Only write the 'private:' keyword if a nocopy method exists
            # and this is not an abstract class.
            wrote_private = False
            if not abstract_class:
                for function_info in function_info_list:
                    if not function_info.write_the_implementation():
                        if not wrote_private:
                            wrote_private = True
                            class_definition_file.write('\n')
                            class_definition_file.write('private:\n')
                            in_class_header_separator_text = '    //------------------------------------------------------------------'
                            class_definition_file.write('{0}\n'.format(in_class_header_separator_text))
                            class_definition_file.write("    // Don't allow copying instances of this class.\n")
                            class_definition_file.write('{0}\n'.format(in_class_header_separator_text))
                        class_definition_file.write('\n')
                        function_info.write_definition(class_definition_file)
                class_definition_file.write('\n')
            # Write the class definition functions declarations.
            class_definition_file.write('public:\n')
            for function_info in function_info_list:
                if function_info.write_the_implementation():
                    class_definition_file.write('\n')
                    function_info.write_definition(class_definition_file)
            # End the class definition.
            class_definition_file.write('};\n\n')
            # Close the conditional include statement
            class_definition_file.write('#endif\n')
            # Close the class definition file.
            print 'Created class definition file {0}.'.format(class_definition_file_name)
        #--------------------------------------------------------------
        # Write the class implementation file.
        #--------------------------------------------------------------
        # Determine if there are any non-inline methods.
        has_non_inline_methods = False
        for function_info in function_info_list:
            if not function_info.is_inline():
                has_non_inline_methods = True
        # If all methods are inline methods or this a pure abstract class
        # then there is no implementation file.
        if has_non_inline_methods:
            # Open the class implementation file.
            with open(class_implementation_file_name, 'w') as class_implementation_file:
                # Write the class implementation file header.
                class_implementation_file.write('{0}\n'.format(stars_text))
                class_implementation_file.write('// Class Implementation File: {0}\n'.format(class_implementation_file_name))
                class_implementation_file.write('// Author: {0}\n'.format(author))
                class_implementation_file.write('// Date: {0}\n'.format(date_text))
                class_implementation_file.write('//\n')
                class_implementation_file.write('// Abstract:\n')
                class_implementation_file.write('//\n')
                class_implementation_file.write('//   This file contains the class implementation for class {0}.\n'.format(class_name))
                class_implementation_file.write('//\n')
                class_implementation_file.write('// Copyright (c) {0}, {1}.\n'.format(year_text, author))
                class_implementation_file.write('//\n')
                class_implementation_file.write('{0}\n\n'.format(stars_text))
                # Write the class implementation include statements.
                # Write the bracketed include statements first.
                # Write the line to include the class header file.
                class_implementation_file.write('#include "{0}.h\"\n'.format(class_name))
                # Write the include files lines for file names that are bracketed, such as '#include <vector>'.
                for include_name in implementation_class_name_set:
                    if include_name[0] == '<':
                        class_implementation_file.write('#include {0}\n'.format(include_name))
                # Write the include files lines for ordinary file names, such as '#include "Foo.h"'.
                for include_name in implementation_class_name_set:
                    if include_name[0] != '<':
                        if '.h' not in include_name:
                            include_name = '{0}.h'.format(include_name)
                        class_implementation_file.write('#include "{0}"\n'.format(include_name))
                # Determine if there are any static data member declarations.
                has_static_data_member = False
                # Determine if there are any static data members.
                for data_member_type_and_name_info in data_member_type_and_name_info_list:
                    type_info = data_member_type_and_name_info.get_type_info()
                    if type_info.get_static_virtual_qualifier_type() == type_info.STATIC_QUALIFIER_TYPE:
                        has_static_data_member = True
                # Are there any static data members?
                if has_static_data_member:
                    # Write the implementation static data member
                    # declarations.  First write the section header.
                    class_implementation_file.write('\n')
                    class_implementation_file.write('{0}\n'.format(function_header_separator_text))
                    class_implementation_file.write('// Static data member declarations\n')
                    class_implementation_file.write('{0}\n\n'.format(function_header_separator_text))
                    # Write the declaration for each static data member.
                    for data_member_type_and_name_info in data_member_type_and_name_info_list:
                        type_info = data_member_type_and_name_info.get_type_info()
                        if type_info.get_static_virtual_qualifier_type() == type_info.STATIC_QUALIFIER_TYPE:
                            # Put the '<classname>::' in front of the variable name.
                            static_variable_name = '{0}::{1}'.format(class_name, data_member_type_and_name_info.get_name())
                            static_data_type_and_name_info = TypeAndNameInfo()
                            static_data_type_and_name_info.set_name(static_variable_name)
                            # If no value is specified for the type and the type is a pointer type, then set the value to 'NULL'.
                            # If the type is a pointer type then set the data member to NULL.
                            static_data_member_value = data_member_type_and_name_info.get_value()
                            if static_data_member_value:
                                static_data_type_info = data_member_type_and_name_info.get_type_info()
                                type_modifier_text = static_data_type_info.get_type_modifier()
                                if  type_modifier_text == '*' or type_modifier_text == '**':
                                    static_data_type_and_name_info.set_value('NULL')
                            static_declaration_text = data_member_type_and_name_info.get_type_and_name_text(TypeInfo.RENDER_IMPLEMENTATION_OR_ARGUMENT_TYPE,
                                                                                                            TypeAndNameInfo.RENDER_VALUE)
                            class_implementation_file.write('{0};\n'.format(static_declaration_text))
                # Write the class implementation function
                # declarations.
                for function_info in function_info_list:
                    if function_info.write_the_implementation():
                        function_info.write_implementation_header(class_implementation_file,
                                                                  class_name,
                                                                  function_header_separator_text,
                                                                  full_header)
                        function_info.write_implementation(class_implementation_file,
                                                           data_member_type_and_name_info_list,
                                                           class_name)
                print 'Created class implementation file {0}.'.format(class_implementation_file_name)
    return 0

