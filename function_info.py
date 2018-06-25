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

from type_info import TypeInfo
from type_and_name_info import TypeAndNameInfo

class FunctionInfo:

    METHOD_NO_COPY_CONSTRUCTOR = 0
    METHOD_NO_COPY_OPERATOR_EQUAL = 1
    METHOD_CONSTRUCTOR = 2
    METHOD_COPY_CONSTRUCTOR = 3
    METHOD_DESTRUCTOR = 4
    METHOD_OPERATOR_EQUAL = 5
    METHOD_COPY = 6
    METHOD_FUNCTION = 7
    
    comment_spacing = 24

    def __init__(self, method_type_and_name_info):
        self.argument_type_and_name_list = []
        self.body_list = []
        self.method_type_and_name_info = method_type_and_name_info
        self.qualifier_text = ''
        self.method_type = FunctionInfo.METHOD_FUNCTION
        self.is_inline_method = False
        self.write_implementation_flag = True

    def is_inline(self):
        return self.is_inline_method

    def set_inline(self, is_inline):
        self.is_inline_method = is_inline

    def get_method_type(self):
        return self.method_type

    def set_method_type(self, method_type):
        self.method_type = method_type

    def get_qualifier(self):
        return self.qualifier_text

    def set_qualifier(self, qualifier_text):
        qualifier_text.strip()
        self.qualifier_text = qualifier_text

    def write_the_implementation(self):
        return self.write_implementation_flag

    def set_write_the_implementation(self, write_implementation_flag):
        self.write_implementation_flag = write_implementation_flag
        
    def get_method_type_and_name_info(self):
        return self.method_type_and_name_info

    def add_argument(self, argument_type_and_name_info):
        self.argument_type_and_name_list.append(argument_type_and_name_info)

    def write_definition(self, output_file):
        #  Write the return type and the function name.
        function_line_text = ''
        the_type_info = self.method_type_and_name_info.get_type_info()
        method_name = self.method_type_and_name_info.get_name()
        definition_return_type_text = the_type_info.get_type_text(TypeInfo.RENDER_DEFINITION_METHOD_RETURN_TYPE)
        if not definition_return_type_text:
            function_line_text = '{0}('.format(method_name)
        else:
            # The string 'definition_return_type_text' is not empty.
            def_return_type_text_len = len(definition_return_type_text)
            if not definition_return_type_text[def_return_type_text_len - 1].isspace():
                definition_return_type_text = '{0} '.format(definition_return_type_text)
            function_line_text = '{0}{1}('.format(definition_return_type_text, method_name)
        #  Test for an inline function.
        if self.is_inline():
            function_line_text = 'inline {0}'.format(function_line_text)
        #  Add leading spaces for the class definition.
        function_line_text = '    {0}'.format(function_line_text)
        #  Get the length of the function declaration.
        function_line_length = len(function_line_text)
        #--------------------------------------------------------------
        #  Write the function signature.
        #--------------------------------------------------------------
        output_file.write(function_line_text);
        if self.argument_type_and_name_list:
            #  Write out the argument list.
            first_flag = True
            # Get the leading spaces text for the arguments.
            spaces_text = ''
            for i in xrange(0, function_line_length):
                spaces_text = '{0} '.format(spaces_text)
            # Write each method argument.
            for argument_type_and_name_info in self.argument_type_and_name_list:
                arg_line_text = argument_type_and_name_info.get_type_and_name_text(TypeInfo.RENDER_DEFINITION_DATA_TYPE,
                                                                                   TypeAndNameInfo.RENDER_VALUE)
                if first_flag:
                    first_flag = False
                else:
                    arg_line_text = ',\n{0}{1}'.format(spaces_text, arg_line_text)
                output_file.write(arg_line_text)
        output_file.write(')')
        #  Write any function qualifiers.

        if self.qualifier_text and not ':' in self.qualifier_text:
            output_file.write(' {0}'.format(self.qualifier_text))
        #  If this is an inline function then write the function body inline.
        if self.is_inline():
            self.write_body(output_file)
        else:
            output_file.write(';\n')

    def write_implementation_header(self,
                                    output_file,
                                    class_name_text,
                                    header_separator_text,
                                    write_full_header_info):
        #  Only write the function header if this is NOT an inline function.
        if not self.is_inline():
            #  Set up header strings.self.method_type_and_name_info.get_name()
            method_name = self.method_type_and_name_info.get_name()
            function_name_text = '{0}::{1}'.format(class_name_text, method_name)
            declare_name_text = ''
            if self.method_type == FunctionInfo.METHOD_CONSTRUCTOR:
                declare_name_text = '//  Constructor: {0}'.format(function_name_text)
            elif self.method_type == FunctionInfo.METHOD_COPY_CONSTRUCTOR:
                declare_name_text = '//  Copy Constructor: {0}'.format(function_name_text)
            elif self.method_type == FunctionInfo.METHOD_DESTRUCTOR:
                declare_name_text = '//  Destructor: {0}'.format(function_name_text)
            elif self.method_type == FunctionInfo.METHOD_OPERATOR_EQUAL:
                declare_name_text = '//  Operator: {0}'.format(function_name_text)
            elif self.method_type == FunctionInfo.METHOD_COPY or self.method_type == FunctionInfo.METHOD_FUNCTION:
                the_type_info = self.method_type_and_name_info.get_type_info()
                if the_type_info.get_static_virtual_qualifier_type() != TypeInfo.STATIC_QUALIFIER_TYPE:
                    declare_name_text = '//  Member Function: {0}'.format(function_name_text)
                else:
                    declare_name_text = '//  Static Member Function: {0}'.format(function_name_text)
            #  Write the class implementation function header.
            output_file.write('\n')
            output_file.write('{0}\n'.format(header_separator_text))
            output_file.write('{0}\n'.format(declare_name_text))
            if self.method_type == FunctionInfo.METHOD_FUNCTION:
                output_file.write('//\n')
                output_file.write('//  Abstract:\n')
                output_file.write('//\n')
                output_file.write('//      This method xxxxxx\n')
            elif self.method_type == FunctionInfo.METHOD_COPY_CONSTRUCTOR:
                output_file.write('//\n')
                output_file.write('//  Abstract:\n')
                output_file.write('//\n')
                output_file.write('//      This copy constructor copies the passed class instance to this class instance.\n')
            elif self.method_type == FunctionInfo.METHOD_OPERATOR_EQUAL:
                output_file.write('//\n')
                output_file.write('//  Abstract:\n')
                output_file.write('//\n')
                output_file.write('//      This equals operator copies the passed class instance to this class instance\n')
                output_file.write('//      and returns this class instance.\n')
            elif self.method_type == FunctionInfo.METHOD_COPY:
                output_file.write('//\n')
                output_file.write('//  Abstract:\n')
                output_file.write('//\n')
                output_file.write('//      This method copies the passed class instance.\n')
            if write_full_header_info:
                the_return_type_info = self.method_type_and_name_info.get_type_info()
                implementation_return_type_text = the_return_type_info.get_type_text(TypeInfo.RENDER_IMPLEMENTATION_OR_ARGUMENT_TYPE)
                #  Write the input argument list.
                if self.method_type != FunctionInfo.METHOD_DESTRUCTOR:
                    if not self.argument_type_and_name_list:
                        if self.method_type != FunctionInfo.METHOD_CONSTRUCTOR:
                            output_file.write('//\n')
                            output_file.write('//\n')
                            output_file.write('//  Input:\n')
                            output_file.write('//\n')
                            output_file.write('//    None.\n')
                            output_file.write('//\n')
                    else:
                        output_file.write('//\n')
                        output_file.write('//\n')
                        output_file.write('//  Input:\n')
                        output_file.write('//\n')
                        for arg_type_and_name_info in self.argument_type_and_name_list:
                            arg_line_text = '//    {0}  '.format(arg_type_and_name_info.get_name())
                            if len(arg_line_text) < FunctionInfo.comment_spacing:
                                spaces_to_add_count = FunctionInfo.comment_spacing - len(arg_line_text)
                                for i in xrange(0, spaces_to_add_count):
                                   arg_line_text = '{0} '.format(arg_line_text)
                            # Get the argument type.
                            arg_type_info = arg_type_and_name_info.get_type_info()
                            if arg_type_info.get_type_modifier() == '&':
                                output_file.write('{0}A reference to a value of type {1}'.format(arg_line_text, arg_type_info.get_name()))
                            elif arg_type_info.get_type_modifier() == '*':
                                output_file.write('{0}A pointer to a value of type {1}'.format(arg_line_text, arg_type_info.get_name()))
                            elif arg_type_info.get_type_modifier() == '**' or arg_type_info.get_type_modifier() == '* *':
                                output_file.write('{0}A pointer to a pointer to a value of type {1}'.format(arg_line_text, arg_type_info.get_name()))
                            elif arg_type_info.get_type_modifier() == '&*' or arg_type_info.get_type_modifier() == '& *':
                                output_file.write('{0}A reference to a pointer to a value of type {1}'.format(arg_line_text, arg_type_info.get_name()))
                            else:
                                output_file.write('{0}A value of type {1}'.format(arg_line_text, arg_type_info.get_name()))
                            if (self.method_type != FunctionInfo.METHOD_COPY_CONSTRUCTOR
                                and self.method_type != FunctionInfo.METHOD_OPERATOR_EQUAL
                                and self.method_type != FunctionInfo.METHOD_COPY):
                                output_file.write(' that xxxxxx\n')
                            else:
                                output_file.write('.\n')
                            output_file.write('//\n')
                        output_file.write('//\n')
                    #  Write the output return specification.
                    if (self.method_type == FunctionInfo.METHOD_FUNCTION
                        and implementation_return_type_text
                        and the_return_type_info.get_name() != 'void'
                        and the_return_type_info.get_name() != 'VOID'
                        and not the_return_type_info.get_type_modifier()):
                        output_file.write('//  Return value:\n')
                        output_file.write('//\n')
                        if the_return_type_info.get_type_modifier() == '&':
                            output_file.write('//    This method returns a reference to a value of type {0} that xxxxxx\n'.format(the_return_type_info.get_name()))
                        elif the_return_type_info.get_type_modifier() == '*':
                            output_file.write('//    This method returns a pointer to a value of type {0} that xxxxxx\n'.format(the_return_type_info.get_name()))
                        elif the_return_type_info.get_type_modifier() == '**':
                            output_file.write('//    This method returns a pointer to a pointer to a value of type {0} that xxxxxx\n'.format(the_return_type_info.get_name()))
                        elif the_return_type_info.get_type_modifier() == '&*':
                            output_file.write('//    This method returns a reference to a pointer to a value of type {0} that xxxxxx\n'.format(the_return_type_info.get_name()))
                        else:
                            output_file.write('//    This method returns a value of type {0} that xxxxxx\n'.format(the_return_type_info.get_name()))
                        output_file.write('//\n')
            output_file.write('{0}\n'.format(header_separator_text))
            output_file.write('\n')

    def write_implementation(self, 
                             output_file,
                             data_member_type_and_name_info_list,
                             class_name_text):
        #  Only write the function body if this is NOT an inline function.
        if not self.is_inline():
            method_type_info = self.method_type_and_name_info.get_type_info()
            implementation_return_type_text = method_type_info.get_type_text(TypeInfo.RENDER_IMPLEMENTATION_OR_ARGUMENT_TYPE)
            #  Write the return type and the function name.
            function_line_text = ''
            if not implementation_return_type_text:
                function_line_text = class_name_text
            else:
                function_line_text = '{0} {1}'.format(implementation_return_type_text, class_name_text)
            function_line_text = '{0}::{1}('.format(function_line_text, self.method_type_and_name_info.get_name())
            #  Get the length of the function declaration.
            function_line_length = len(function_line_text)
            #  Write the function line.
            output_file.write(function_line_text)
            # Are there any function arguments?
            if len(self.argument_type_and_name_list) > 0:
                #  Write out the argument list.
                first_flag = True
                spaces_text = ''
                for i in xrange(0, function_line_length):
                    spaces_text = '{0} '.format(spaces_text)
                for arg_type_and_name in self.argument_type_and_name_list:
                    arg_line_text = arg_type_and_name.get_type_and_name_text(TypeInfo.RENDER_IMPLEMENTATION_OR_ARGUMENT_TYPE,
                                                                             TypeAndNameInfo.RENDER_NO_VALUE)
                    if first_flag:
                        first_flag = False
                    else:
                        arg_line_text = ',\n{0}{1}'.format(spaces_text, arg_line_text)
                    output_file.write(arg_line_text)
                output_file.write(')')
            else:
                output_file.write(')')
            #  Write any function qualifiers.
            if self.qualifier_text:
                output_file.write(' {0}'.format(self.qualifier_text))
            output_file.write('\n')
            #  If this function is a constructor then write the
            #  data member initialization list.
            if self.method_type == FunctionInfo.METHOD_CONSTRUCTOR:
                first_data_member = True
                for data_mem_type_and_name_info in data_member_type_and_name_info_list:
                    # Don't initialize static data members in the constructor member initialization list.
                    data_mem_type_info = data_mem_type_and_name_info.get_type_info()
                    if data_mem_type_info.get_static_virtual_qualifier_type() != TypeInfo.STATIC_QUALIFIER_TYPE:
                        # If a default value is supplied then use it.
                        default_value_text = data_mem_type_and_name_info.get_value()
                        # If the type is a pointer type then set the default value to NULL.
                        if not default_value_text:
                            type_modifier_text = data_mem_type_info.get_type_modifier()
                            initialize_data_member = type_modifier_text == '*' or type_modifier_text == '**'
                            if type_modifier_text == '*' or type_modifier_text == '**':
                                default_value_text = 'NULL'
                        # Should the data member should be initialized?
                        if default_value_text:
                            if first_data_member:
                                first_data_member = False
                                output_file.write('  : ')
                            else:
                                output_file.write('  , ')
                            output_file.write('{0}({1})\n'.format(data_mem_type_and_name_info.get_name(), default_value_text))
            #  Write the function body.
            self.write_body(output_file)
            output_file.write('\n')

    def add_body_text(self, text):
        self.body_list.append(text)

    def write_body(self, output_file):
        # Write the function body.
        for text in self.body_list:
            output_file.write(text)

    def has_body(self):
        return len(self.body_list) > 0

    def clear(self):
        self.argument_type_and_name_list = []
        self.body_list = []
        self.method_type_and_name_info = type_and_name
        self.qualifier_text = ''
        self.method_type = METHOD_FUNCTION
        self.is_inline_method = False
        self.write_implementation_flag = True
