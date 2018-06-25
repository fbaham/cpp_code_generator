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

from file_buffer import FileBuffer
from type_info import TypeInfo
from type_and_name_info import TypeAndNameInfo
from function_info import FunctionInfo
from include_file_manager import IncludeFileManager

class Bparse:

    DATA_STATE = 0
    FUNCTION_SIGNATURE_STATE = 1
    FUNCTION_BODY_STATE = 2

    def __init__(self, input_file):
        self.parser_state = Bparse.DATA_STATE
        self.file_position = 0
        self.line_number = 1
        self.has_inline_keyword = False
        self.has_copy_constructor = False
        self.file_buffer = None
        self.class_name = ''
        self.destructor_name = ''
        self.input_file = input_file
        self.file_buffer = FileBuffer(self.input_file)
        self.file_name_manager = IncludeFileManager()
        self.variable_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
        self.intrinsic_type_checker = TypeInfo()

    def parse(self,
              data_member_type_and_name_info_list,
              definition_class_name_set,
              implementation_class_name_set,
              function_info_list,
              class_name):
        # Parse the entire input file.
        # Save the class name and the destructor name.
        self.class_name = class_name
        self.destructor_name = '~{0}'.format(self.class_name)
        # Point to the first byte of the file.
        self.file_position = 0
        # Initialize parse variables.
        copy_keyword_found_in_input_file = False
        nocopy_keyword_found_in_input_file = False
        the_type_and_name_info = TypeAndNameInfo()
        last_parse_position = -1
        # Loop and parse all characters in the input file.
        while not self.file_buffer.past_end_of_file():
            # Check to see if the parser is unable to consume
            # the current character at 'self.file_position'.
            if last_parse_position == self.file_position:
                raise ValueError('Illegal character on line {0}'.format(self.line_number))
            # Save the current parse position.
            last_parse_position = self.file_position
            # Parse from the current file position.
            if self.parser_state == Bparse.DATA_STATE:
                found_copy_keyword = False
                found_nocopy_keyword = False
                found_property_keyword = False
                # Loop and test for special keywords.
                while True:
                    found_copy_keyword = False
                    found_nocopy_keyword = False
                    found_property_keyword = False
                    # Test for the 'copy:' keyword, which, if found, will result in the
                    # copy constructor, operator=, and a Copy method being created.
                    # The Copy method pointer is returned here instead of a boolean
                    # because the Copy method body cannot be written until all the data
                    # members have been parsed.  The Copy method body is written in
                    # this method below outside of the main parse-loop.
                    found_copy_keyword = self._parse_copy(function_info_list)
                    if found_copy_keyword:
                        # A second 'copy:' keyword is not allowed.
                        if copy_keyword_found_in_input_file:
                            raise ValueError('A second copy: keyword is not allowed. line {0}'.format(self.line_number))
                        copy_keyword_found_in_input_file = True
                    # Check for the 'nocopy:' keyword.
                    # The 'copy:' keyword can only be found once, otherwise
                    # the _parse_copy( method throws an exception.
                    found_nocopy_keyword = self._parse_no_copy(function_info_list)
                    if found_nocopy_keyword:
                        # A second 'nocopy:' keyword is not allowed.
                        if nocopy_keyword_found_in_input_file:
                            raise ValueError('A second nocopy: keyword is not allowed. line {0}'.format(self.line_number))
                        nocopy_keyword_found_in_input_file = True
                    # Test for the 'property:' keyword, which results in creating
                    # property get-set methods.
                    found_property_keyword = self._parse_property(data_member_type_and_name_info_list, function_info_list)
                    if not (found_property_keyword or found_copy_keyword or found_nocopy_keyword):
                        break
                # Parse the type and name.
                self.__parse_type_and_name(the_type_and_name_info)
                the_type_info = the_type_and_name_info.get_type_info()
                self._save_include_name(definition_class_name_set,
                                        implementation_class_name_set,
                                        the_type_info)
                if self._current_parser_state() == Bparse.DATA_STATE:
                    # If the parser leaves the data section then 'type_and_name'
                    # can contain an empty type string.  Throw empty type strings away.
                    a_type_info = the_type_and_name_info.get_type_info()
                    type_name = a_type_info.get_name()
                    if type_name:
                        # Save the data member declaration.
                        data_member_type_and_name_info_list.append(the_type_and_name_info)
                        the_type_and_name_info = TypeAndNameInfo()
            elif self.parser_state == Bparse.FUNCTION_SIGNATURE_STATE:
                self._parse_function(function_info_list,
                                     definition_class_name_set,
                                     implementation_class_name_set,
                                     the_type_and_name_info)
                the_type_and_name_info = TypeAndNameInfo()
            elif self.parser_state == Bparse.FUNCTION_BODY_STATE:
                self._parse_function_body(function_info_list)
            else:
                # Should never arrive here unless there is bug.
                raise ValueError('Illegal parser state.  Line {0}'.format(self.line_number))
        # Don't allow two copy constructors and operator=() methods.
        if copy_keyword_found_in_input_file and nocopy_keyword_found_in_input_file:
            raise ValueError('Cannot use both the copy: and nocopy: keywords.  Line {0}'.format(self.line_number))
        # If the the 'copy:' keyword was used, then fill in the Copy
        # method body now that all the data members have been parsed.
        if copy_keyword_found_in_input_file:
            # Find the Copy method that was produced by the copy keyword.
            for the_function_info in function_info_list:
                # Is this function the 'Copy' function produced by the 'copy:' keyword?
                if the_function_info.get_method_type() == FunctionInfo.METHOD_COPY:
                    self._set_copy_method_body(the_function_info, data_member_type_and_name_info_list)
        # Sort the function names.  The order is constructors, copy constructor, destructor,
        # operator equals, and then other methods.
        function_info_list.sort(key=lambda finfo: finfo.get_method_type())

    def get_line_number(self):
        return self.line_number

    def _parse_copy(self, function_info_list):
        self._skip_white_space()
        # Test for the 'copy:' keyword.
        has_copy = self._test_for_token('copy:')
        if has_copy:
            # Don't allow two copy constructors.
            if not self.has_copy_constructor:
                self.has_copy_constructor = True
                #  Create the copy constructor.
                copy_constructor_the_type_and_name_info = TypeAndNameInfo()
                # Leave the type the empty string for the return type of the constructor.
                copy_constructor_the_type_and_name_info.set_name(self.class_name)
                copy_constructor_function_info = FunctionInfo(copy_constructor_the_type_and_name_info)
                copy_argument_type_info = TypeInfo()
                copy_argument_type_info.set_const_volatile_qualifier_type(TypeInfo.CONST_QUALIFIER_TYPE)
                copy_argument_type_info.set_name(self.class_name)
                copy_argument_type_info.set_type_modifier('&')
                copy_argument_type_and_name_info = TypeAndNameInfo()
                copy_argument_type_and_name_info.set_type_info(copy_argument_type_info)
                copy_argument_type_and_name_info.set_name('that')
                # Add the argument to the copy constructor.
                # The copy constructor, operator =, and the Copy() method all use
                # 'copy_argument_type' for the function argument.
                copy_constructor_function_info.add_argument(copy_argument_type_and_name_info)
                # Create the copy constructor function body.
                copy_constructor_function_info.add_body_text('{\n    Copy(that);\n}')
                # Set the method type.
                copy_constructor_function_info.set_method_type(FunctionInfo.METHOD_COPY_CONSTRUCTOR)
                # Add the copy constructor to the function pointer list.
                function_info_list.append(copy_constructor_function_info)
                #  Create operator =.
                operator_equal_return_type_info = TypeInfo()
                operator_equal_return_type_info.set_name(self.class_name)
                operator_equal_return_type_info.set_type_modifier('&')
                operator_equal_the_type_and_name_info = TypeAndNameInfo()
                operator_equal_the_type_and_name_info.set_type_info(operator_equal_return_type_info)
                operator_equal_the_type_and_name_info.set_name('operator =')
                operator_equal_function_info = FunctionInfo(operator_equal_the_type_and_name_info)
                # Add the argument to 'operator equal'.
                operator_equal_function_info.add_argument(copy_argument_type_and_name_info)
                # Create the 'operator equal' function body.
                operator_equal_function_info.add_body_text('{\n')                
                operator_equal_function_info.add_body_text('    // TODO: Consider testing for inequality by value.\n')
                operator_equal_function_info.add_body_text('    //if (*this != *that)\n')
                operator_equal_function_info.add_body_text('    if (this != &that)\n')
                operator_equal_function_info.add_body_text('    {\n')
                operator_equal_function_info.add_body_text('        Copy(that);\n')
                operator_equal_function_info.add_body_text('    }\n')
                operator_equal_function_info.add_body_text('\n    return *this;\n')
                operator_equal_function_info.add_body_text('}')
                # Set the method type.
                operator_equal_function_info.set_method_type(FunctionInfo.METHOD_OPERATOR_EQUAL)
                # Add the 'operator =' method to the function pointer list.
                function_info_list.append(operator_equal_function_info)
                #  Create the Copy method.
                copy_method_return_type_info = TypeInfo()
                copy_method_return_type_info.set_name('void')
                copy_method_the_type_and_name_info = TypeAndNameInfo()
                copy_method_the_type_and_name_info.set_type_info(copy_method_return_type_info)
                copy_method_the_type_and_name_info.set_name('Copy')
                copy_method_info = FunctionInfo(copy_method_the_type_and_name_info)
                # Add the argument to the copy constructor.
                copy_method_info.add_argument(copy_argument_type_and_name_info)
                # The Copy function body is set later in the Bparse.parse() method after
                # all of the data members have been parsed.
                # Set the method type.
                copy_method_info.set_method_type(FunctionInfo.METHOD_COPY)
                # Add the Copy function to the function pointer list.
                function_info_list.append(copy_method_info)
            else:
                raise ValueError('The copy: and the nocopy: keyword cannot be used together or more than once.   Line {0}.'.format(self.line_number))
        return has_copy

    def _parse_no_copy(self, function_info_list):
        self._skip_white_space()
        # Test for the 'nocopy:' keyword.
        has_nocopy = self._test_for_token('nocopy:')
        if has_nocopy:
            # Don't allow two copy constructors.
            if not self.has_copy_constructor:
                self.has_copy_constructor = True
                # Create the 'nocopy' copy constructor.
                #Type copy_constructor_return_type
                #copy_constructor_return_type->set_name('')
                #copy_constructor_type_and_name.set_type_info(copy_constructor_return_type)
                copy_constructor_the_type_and_name_info = TypeAndNameInfo()
                copy_constructor_the_type_and_name_info.set_name(self.class_name)
                copy_constructor_function_info = FunctionInfo(copy_constructor_the_type_and_name_info)
                copy_argument_type_info = TypeInfo()
                copy_argument_type_info.set_const_volatile_qualifier_type(TypeInfo.CONST_QUALIFIER_TYPE)
                copy_argument_type_info.set_name(self.class_name)
                copy_argument_type_info.set_type_modifier('&')
                copy_argument_type_and_name_info = TypeAndNameInfo()
                copy_argument_type_and_name_info.set_type_info(copy_argument_type_info)
                copy_argument_type_and_name_info.set_name('that')
                # Add the argument to the copy constructor.
                # The copy constructor, operator =, and the Copy() method all use
                # 'copy_argument_type' for the function argument.
                copy_constructor_function_info.add_argument(copy_argument_type_and_name_info)
                # Do not call the FunctionInfo.add_body_text method.  Don't implement the method.
                # Setting to 'not write' the implementation will also result in the
                # 'private: keyword being written.
                copy_constructor_function_info.write_the_implementation(False)
                # Set the method type.
                copy_constructor_function_info.set_method_type(FunctionInfo.METHOD_NO_COPY_CONSTRUCTOR)
                # Add the copy constructor to the function pointer list.
                function_info_list.append(copy_constructor_function_info)
                #  Create the 'nocopy' operator =.
                operator_equal_return_type_info = TypeInfo()
                operator_equal_return_type_info.set_name(self.class_name)
                operator_equal_return_type_info.set_type_modifier('&')
                operator_equal_the_type_and_name_info = TypeAndNameInfo()
                operator_equal_the_type_and_name_info.set_type_info(operator_equal_return_type_info)
                operator_equal_the_type_and_name_info.set_name('operator =')
                operator_equal_function_info = FunctionInfo(operator_equal_the_type_and_name_info)
                # Add the argument to 'operator equal'.
                operator_equal_function_info.add_argument(copy_argument_type_and_name_info)
                # Do not call the FunctionInfo.add_body_text method.  Don't implement the method.
                operator_equal_function_info.write_the_implementation(False)
                # Set the method type.
                operator_equal_function_info.set_method_type(FunctionInfo.METHOD_NO_COPY_OPERATOR_EQUAL)
                # Add the 'operator =' method to the function pointer list.
                function_info_list.append(operator_equal_function_info)
            else:
                raise ValueError('The copy: and the nocopy: keyword cannot be used together or more than once.  Line {0}.'.format(self.line_number))
        return has_nocopy

    def _parse_property(self, 
                        data_member_type_and_name_info_list,
                        function_info_list):
        self._skip_white_space()
        # Test for the 'property:' keyword.
        has_property = self._test_for_token('property:')
        if has_property:
            # This is a property.
            property_the_type_and_name_info = TypeAndNameInfo()
            self.__parse_type_and_name(property_the_type_and_name_info)
            function_name_text = self._get_variable_name()
            if not function_name_text:
                raise ValueError('Missing function name in property.  Line {0}'.format(self.line_number))
            a_type_info = property_the_type_and_name_info.get_type_info()
            type_name = a_type_info.get_name()
            if not type_name:
                raise ValueError('Missing type in property.  Line {0}.'.format(self.line_number))
            # Use the property name as the variable name.
            data_member_name_text = property_the_type_and_name_info.get_name()
            if not data_member_name_text:
                raise ValueError('Missing name in property.  Line {0}.'.format(self.line_number))
            # Create the data member.
            data_member_type_and_name_info = TypeAndNameInfo()
            data_member_type_and_name_info.set_type_info(property_the_type_and_name_info.get_type_info())
            data_member_type_and_name_info.set_name(property_the_type_and_name_info.get_name())
            # Add the data member to the data string list.
            data_member_type_and_name_info_list.append(data_member_type_and_name_info)
            # Create the 'get' property method.
            get_function_the_type_and_name_info = TypeAndNameInfo()
            get_function_the_type_and_name_info.set_type_info(property_the_type_and_name_info.get_type_info())
            get_function_the_type_and_name_info.set_name(function_name_text)
            get_function_info = FunctionInfo(get_function_the_type_and_name_info)
            # Make the method a 'const' method.
            get_function_info.set_qualifier('const')
            # Create the 'get' property function body.
            get_function_info.add_body_text('{\n    return ')
            get_function_info.add_body_text(data_member_name_text)
            get_function_info.add_body_text('\n}')
            # Add the 'get' property method to the function pointer list.
            function_info_list.append(get_function_info)
            # Create the 'set' property method.
            set_function_the_type_and_name_info = TypeAndNameInfo()
            set_type_info = TypeInfo()
            set_type_info.set_name('void')
            set_function_the_type_and_name_info.set_type_info(set_type_info)
            set_method_name_text = 'set{0}'.format(function_name_text)
            set_function_the_type_and_name_info.set_name(set_method_name_text)
            set_function_info = FunctionInfo(set_function_the_type_and_name_info)
            # Create the function argument list.
            argument_type_info = property_the_type_and_name_info.get_type_info()
            type_name = argument_type_info.get_name()
            type_modifiers = argument_type_info.get_type_modifier()
            # If there is a type modifier, the propertie's set method has a
            # 'const' argument. If not an intrinsic type, then pass the const
            # parameter as a reference.
            if self._is_intrinsic_type(type_name):
                if type_modifiers:
                    argument_type_info.set_const_volatile_qualifier_type(TypeInfo.CONST_QUALIFIER_TYPE)
            else:
                argument_type_info.set_const_volatile_qualifier_type(TypeInfo.CONST_QUALIFIER_TYPE)
                if not type_modifiers:
                    argument_type_info.set_type_modifier('&')
            argument_type_and_name_info = TypeAndNameInfo()
            argument_type_and_name_info.set_type_info(argument_type_info)
            set_argument_variable_name = 'the_value'
            argument_type_and_name_info.set_name(set_argument_variable_name)
            set_function_info.add_argument(argument_type_and_name_info)
            # Create the 'set' property function body.
            set_function_info.add_body_text('{\n    ')
            set_function_info.add_body_text(data_member_name_text)
            set_function_info.add_body_text(' = ')
            set_function_info.add_body_text(set_argument_variable_name)
            set_function_info.add_body_text('\n}')
            # Add the 'set' property method to the function pointer list.
            function_info_list.append(set_function_info)
            self._skip_white_space()
            # Skip any optional terminating semicolon character.
            if self.file_buffer[self.file_position] == ';':
                self.file_position += 1
        return has_property

    def __parse_type_and_name(self, the_type_and_name_info):
        #the_type_and_name_info.Clear()
        # Get the type.
        the_type_info = TypeInfo()
        self._parse_type(the_type_info)
        the_type_and_name_info.set_type_info(the_type_info)
        self._skip_white_space()
        # The type has been found.  Next get the variable name or a function name.
        # If the type name is the empty string then look for either
        # '@()' and '~@()' for a constructor and destructor respectively'
        name = the_type_info.get_name()
        if not name:
            if self.file_buffer[self.file_position] == '@':
                self.file_position += 1
                self._skip_white_space()
                if self.file_buffer[self.file_position] == '(':
                    # A constructor was found.
                    self.file_position += 1
                    the_type_and_name_info.set_name(self.class_name)
                    self._skip_white_space()
                    self._set_parser_state(Bparse.FUNCTION_SIGNATURE_STATE)
                else:
                    # If here, then the variable name is '@'.  The symbol
                    # @ represents the class name and is not a valid variable
                    # name.  Throw an exception.
                    raise ValueError('The classname-symbol @ may not be used as a variable name.  Line {0}.'.format(self.line_number))
            elif self.file_buffer[self.file_position] == '~' and self.file_buffer[self.file_position + 1] == '@':
                self.file_position += 2
                self._skip_white_space()
                if self.file_buffer[self.file_position] == '(':
                    # The destructor was found.
                    self.file_position += 1
                    destructor_name_text = '~{0}'.format(self.class_name)
                    the_type_and_name_info.set_name(destructor_name_text)
                    self._skip_white_space()
                    self._set_parser_state(Bparse.FUNCTION_SIGNATURE_STATE)
                else:
                    raise ValueError('Malformed destructor.  Line {0}.'.format(self.line_number))
        else:
            # Get the variable name.
            variable_name = self._get_variable_name()
            the_type_and_name_info.set_name(variable_name)
            self._skip_white_space()
            c = self.file_buffer[self.file_position]
            # Test to see if this is the start of a function.
            if c == '(':
                # This is a function.  A function always starts with a type and name.
                # Skip the opening parenthesis and the Function parser will start parsing.
                # the argument list.
                self.file_position += 1
                self._skip_white_space()
                self._set_parser_state(Bparse.FUNCTION_SIGNATURE_STATE)
            # Check for a default value.
            elif c == '=':
                self.file_position += 1
                value_text = ''
                value_text = self._get_value_text()
                the_type_and_name_info.set_value(value_text)
                # Get the next character for below.
                c = self.file_buffer[self.file_position]
                # Test for the line termination character.
                if c == ';':
                    # Skip the terminating semicolon.  The rendering code will add it back.
                    self.file_position += 1
                    self._skip_white_space()
            elif c == ';':
                self.file_position += 1
        self._skip_white_space()

    def _parse_type(self, the_type_info):
        # Test for the 'virtual' and 'static' keywords.
        self._parse_static_virtual_qualifier_type(the_type_info)
        # Test for the 'const' and 'volatile' keywords.
        self._parse_const_volatile_qualifier_type(the_type_info)
        # Get the name of the type.
        self._get_type_name(the_type_info)
        # Get any type modifiers, such as '*', or '&'.
        # There can be more than one type modifier.  This program
        # does not allow type modifiers to be declared with the
        # 'const' or 'volatile' keywords.
        self._get_type_modifier_tokens(the_type_info)

    def _parse_static_virtual_qualifier_type(self, the_type_info):
        self._skip_white_space()
        # Check for the inline keyword.  The 'inline' keyword can only apply
        # to methods and is not stored as part of the 'type'.
        self.has_inline_keyword = self._test_for_token('inline')
        # The 'virtual' and 'static' keywords cannot both be used to declare a type.
        if self._test_for_token('virtual'):
            the_type_info.set_static_virtual_qualifier_type(TypeInfo.VIRTUAL_QUALIFIER_TYPE)
        elif self._test_for_token('static'):
            the_type_info.set_static_virtual_qualifier_type(TypeInfo.STATIC_QUALIFIER_TYPE)
        else:
            the_type_info.set_static_virtual_qualifier_type(TypeInfo.NORMAL_QUALIFIER_TYPE)

    def _parse_const_volatile_qualifier_type(self, the_type_info):
        self._skip_white_space()
        # The 'const' and 'volatile' keywords cannot both be used to declare a type.
        if self._test_for_token('const'):
            the_type_info.set_const_volatile_qualifier_type(TypeInfo.CONST_QUALIFIER_TYPE)
        elif self._test_for_token('volatile'):
             the_type_info.set_const_volatile_qualifier_type(TypeInfo.VOLATILE_QUALIFIER_TYPE)
        else:
            the_type_info.set_const_volatile_qualifier_type(TypeInfo.NORMAL_QUALIFIER_TYPE)

    def _test_for_token(self, token_text):
        found_token_text = False
        self._skip_white_space()
        # Save the file position in case the search fails.
        current_file_position = self.file_position
        token_text_length = len(token_text)
        index = 0
        c = ''
        while not self.file_buffer.past_end_of_file():
            c = self.file_buffer[self.file_position]
            if index < token_text_length:
                if c == token_text[index]:
                    index += 1
                    self.file_position += 1
                else:
                    break
            else:
                # If c is a symbol character here and not a delimiter,
                # the the token string is not considered to be found.
                found_token_text = not c in self.variable_characters
                break
        if not found_token_text:
            # If not found, restore the file position.
            self.file_position = current_file_position
        return found_token_text

    def _get_type_name(self, the_type_info):
        self._skip_white_space()
        type_name_text = ''
        saved_file_position = self.file_position
        # Do a special check for the class name substitution character.
        if self.file_buffer[self.file_position] == '@':
            self.file_position += 1
            self._skip_white_space()
            if self.file_buffer[self.file_position] == '(':
                # A constructor was found.  Set the type name to the empty
                # string. Don't increment past the characters '@('.  The
                # @ character will be converted to the class name later.
                self.file_position = saved_file_position
                type_name_text = ''
            else:
                # Substitute the class name for the '@' character.
                self.file_position += 1
                type_name_text = self.class_name
        elif self.file_buffer[self.file_position] == '~' and self.file_buffer[self.file_position + 1] == '@':
            # A destructor was found.  Set the type name to the empty
            # string. Don't increment past the characters.  The @
            # character will be converted to the class name later.
            self.file_position += 2
            self._skip_white_space()
            if self.file_buffer[self.file_position] == '(':
                self.file_position = saved_file_position
                type_name_text = ''
            else:
                raise ValueError('Malformed destructor.  Line {0}.'.format(self.line_number))
        else:
            type_stack_list = []
            not_first_character = False
            while not self.file_buffer.past_end_of_file():
                c = self.file_buffer[self.file_position]
                if self._test_for_token('unsigned'):
                    type_name_text += 'unsigned '
                    self._skip_white_space()
                elif self._test_for_token('signed'):
                    type_name_text += 'signed '
                    self._skip_white_space()
                elif c in self.variable_characters:
                    self.file_position += 1
                    type_name_text = '{0}{1}'.format(type_name_text, c)
                elif c == ':' and self.file_buffer[self.file_position + 1] == ':':
                    self.file_position += 2
                    type_name_text = '{0}::'.format(type_name_text)
                elif (c in self.variable_characters
                      or (not_first_character and c.isdigit())
                      or c == '_'):
                    self.file_position += 1
                    not_first_character = True
                    type_name_text = '{0}{1}'.format(type_name_text, c)
                elif c == '<':
                    # Push the expected closing bracket on the type stack.
                    type_stack_list.append('>')
                    self.file_position += 1
                    type_name_text = '{0}{1}'.format(type_name_text, c)
                elif c == '>':
                    self.file_position += 1
                    # Make sure the top of the stack has a closing bracket.
                    if type_stack_list[len(type_stack_list)-1] == '>':
                        # Remove the closing bracket from the top of the stack.
                        type_stack_list.pop()
                        type_name_text = '{0}>'.format(type_name_text)
                    else:
                        raise ValueError('Missing bracket.  Line {0}.'.format(self.line_number))
                elif c == '\n':
                    self.file_position += 1
                    self.line_number += 1
                    break
                # If inside of a template declaration ignore spaces.
                elif c.isspace() and len(type_stack_list) != 0:
                    # Should this be just _skip_white_space()?
                    self._skip_white_space()
                    if self.file_buffer[self.file_position] == '>':
                        self.file_position += 1
                        # Make sure the top of the stack has a closing bracket.
                        if type_stack_list[len(type_stack_list)-1] == '>':
                            # Remove the closing bracket from the top of the stack.
                            type_stack_list.pop()
                            type_name_text = '{0}>'.format(type_name_text)
                        else:
                            raise ValueError('Missing bracket.  Line {0}.'.format(self.line_number))
                    else:
                        # Do not increment self.file_position here so that the current
                        # character can be processed later.
                        break
                elif c == '\n':
                    self.file_position += 1
                    self.line_number += 1
                else:
                    self._skip_white_space()
                    # Do not increment self.file_position here so that the current character
                    # can be processed later.  Skip any terminating semi-colon character.
                    if self.file_buffer[self.file_position] == ';':
                        self.file_position += 1
                    break
            # Make sure that all brackets are closed.
            if len(type_stack_list) != 0:
                raise ValueError('Error on line {0}.'.format(self.line_number))
        the_type_info.set_name(type_name_text)

    def _get_type_modifier_tokens(self, the_type_info):
        # Get any type modifiers.
        type_modifier_text = ''
        test_for_more_type_modifiers = True
        while True:
            self._skip_white_space()
            while not self.file_buffer.past_end_of_file():
                c = self.file_buffer[self.file_position]
                if c == '*':
                    self.file_position += 1
                    type_modifier_text = '{0}{1}'.format(type_modifier_text, c)
                elif c == '&':
                    self.file_position += 1
                    type_modifier_text = '{0}{1}'.format(type_modifier_text, c)
                elif c == '\r' and self.file_buffer[self.file_position + 1] == '\n':
                    self.file_position += 2
                    self.line_number += 1
                elif c == '\n':
                    self.file_position += 1
                    self.line_number += 1
                else:
                    # Do not increment self.file_position here so that the current
                    # character can be processed later.
                    test_for_more_type_modifiers = False
                    break
            if not (test_for_more_type_modifiers and not self.file_buffer.past_end_of_file()):
                break
        the_type_info.set_type_modifier(type_modifier_text)

    def _get_variable_name(self):
        self._skip_white_space()
        variable_name = ''
        not_first_character = False
        c = '\0'
        while not self.file_buffer.past_end_of_file():
            c = self.file_buffer[self.file_position]
            if c in self.variable_characters or (not_first_character and c.isdigit()):
                self.file_position += 1
                not_first_character = True
                variable_name = '{0}{1}'.format(variable_name, c)
            elif c == '\n':
                self.file_position += 1
                self.line_number += 1
                break
            else:
                # Do not increment self.file_position here so that the current
                # character can be processed later.
                break
        self._skip_white_space()
        # Check for an array variable.
        if c == '[':
            # Add everything to the variable until the closing bracket.
            variable_name = '{0}{1}'.format(variable_name, c)
            self.file_position += 1
            while not self.file_buffer.past_end_of_file():
                c = self.file_buffer[self.file_position]
                self.file_position += 1
                variable_name = '{0}{1}'.format(variable_name, c)
                if c == ']':
                    break
                elif c == '\n':
                    self.line_number += 1
        return variable_name

    def _get_value_text(self):
        value_text = ''
        self._skip_white_space()
        if self.file_buffer[self.file_position] == ';':
            self.file_position += 1
        else:
            inside_quoted_text = False
            while not self.file_buffer.past_end_of_file():
                c = self.file_buffer[self.file_position]
                if (c in self.variable_characters
                    or c == '.'
                    or c == '+'
                    or c == '-'):
                    self.file_position += 1
                    value_text = '{0}{1}'.format(value_text, c)
                elif c == '"':
                    self.file_position += 1
                    value_text = '{0}{1}'.format(value_text, c)
                    if inside_quoted_text:
                        break
                    else:
                        inside_quoted_text = True
                elif inside_quoted_text:
                    if c == '\\' and self.file_buffer[self.file_position + 1] == '"':
                        self.file_position += 2
                        value_text = '{0}{1}"'.format(value_text, c)
                    elif c == '\n':
                        raise ValueError('Quoted string not terminated.  Line {0}.'.format(self.line_number))
                    else:
                        self.file_position += 1
                        value_text = '{0}{1}'.format(value_text, c)
                else:
                    # Do not increment self.file_position here so that the current
                    # character can be processed later.
                    break
        return value_text

    def _parse_function(self,
                        function_info_list,
                        definition_class_name_set,
                        implementation_class_name_set,
                        the_type_and_name_info):
        function_info = FunctionInfo(the_type_and_name_info)
        function_name_text = the_type_and_name_info.get_name()
        destructor_name_text = '~{0}'.format(self.class_name)
        # Set the method type.  The copy constructor created by the
        # 'copy:' keyword does not result in _parse_function being called.
        method_type = FunctionInfo.METHOD_FUNCTION
        if function_name_text == self.class_name:
            method_type = FunctionInfo.METHOD_CONSTRUCTOR
        elif function_name_text == destructor_name_text:
            method_type = FunctionInfo.METHOD_DESTRUCTOR
        function_info.set_method_type(method_type)
        self._skip_white_space()
        # Save the file position in case the search fails.
        current_file_position = self.file_position
        c = '\0'
        # Check for a function that takes no parameters.
        while not self.file_buffer.past_end_of_file():
            c = self.file_buffer[self.file_position]
            # Check for the end of the function declaration.
            if c == ')':
                # The function takes no parameters.
                self.file_position += 1
                self._skip_white_space()
                self._set_parser_state(Bparse.FUNCTION_BODY_STATE)
                break
            # Check for a function that takes no parameters that has 'void' as a parameter.
            elif self._test_for_token('void'):
                self._skip_white_space()
                if self.file_buffer[self.file_position] == ')':
                    self.file_position += 1
                    self._skip_white_space()
                    self._set_parser_state(FunctionBodyState)
                break
            else:
                # Do not increment self.file_position here so that the current
                # character can be processed later.
                break
        # If the function took parameters then the code above did not set
        # the parse-state to 'FunctionBodyState'.
        if self._current_parser_state() == Bparse.FUNCTION_SIGNATURE_STATE:
            # Put the file position back to what it was before the loop above ran.
            self.file_position = current_file_position
            # The function takes parameters. Parse the parameters.
            while not self.file_buffer.past_end_of_file():
                argument_type_and_name_info = TypeAndNameInfo()
                self.__parse_type_and_name(argument_type_and_name_info)
                function_info.add_argument(argument_type_and_name_info)
                # Save any class name.
                the_argument_type_info = argument_type_and_name_info.get_type_info()
                self._save_include_name(definition_class_name_set,
                                        implementation_class_name_set,
                                        the_argument_type_info)
                self._skip_white_space()
                c = self.file_buffer[self.file_position]
                if c == ')':
                    self.file_position += 1
                    self._skip_white_space()
                    break
                elif c == ',':
                    # Skip the comma argument delimiter.  Commas will be
                    # added back in the code that renders the C++ code.
                    self.file_position += 1
                self._skip_white_space()
        # Get the function qualifier.  The function qualifier is all the text.
        # up to either the newline character or the opening bracket '{' of the
        # function. This will be either 'const', '=0', '= 0' or just whitespace.
        function_qualifier_text = ''
        # A constructor or the destructor must have an open bracket that starts
        # the function body at this point.
        if method_type != FunctionInfo.METHOD_FUNCTION:
            if self.file_buffer[self.file_position] != '{':
                if method_type == FunctionInfo.METHOD_CONSTRUCTOR:
                    raise ValueError('Error following constructor definition.  Line {0}.'.format(self.line_number))
                else:
                    raise ValueError('Error following destructor definition.  Line {0}.'.format(self.line_number))
        else:
            if self._test_for_token('const'):
                function_qualifier_text = 'const'
            self._skip_white_space()
            if self.file_buffer[self.file_position] == '=':
                self.file_position += 1
                self._skip_white_space()
                if self.file_buffer[self.file_position] == '0':
                    function_qualifier_text = '{0}= 0'.format(function_qualifier_text)
                else:
                    raise ValueError('Illegal pure virtual function definition.  Line {0}.'.format(self.line_number))
            function_qualifier_text.strip()
            self._skip_white_space()
        function_info.set_qualifier(function_qualifier_text)
        function_info.set_inline(self.has_inline_keyword)
        # Add the function to the function pointer list.
        function_info_list.append(function_info)
        self._skip_white_space()
        if self.file_buffer[self.file_position] != '{':
            raise ValueError('Illegal character.  Line {0}.'.format(self.line_number))
        self._set_parser_state(Bparse.FUNCTION_BODY_STATE)

    def _parse_function_body(self, function_info_list):
        self._skip_white_space()
        function_info = function_info_list[len(function_info_list)-1]
        inside_comment = False
        inside_double_quotes = False
        inside_single_quotes = False
        bracket_count = 0
        while not self.file_buffer.past_end_of_file():
            c = self.file_buffer[self.file_position]
            c1 = self.file_buffer[self.file_position + 1]
            function_info.add_body_text(c)
            if c == '/' and c1 == '/':
                inside_comment = True
                function_info.add_body_text(c)
                self.file_position += 2
            if c == '\\' and c1 == '"':
                function_info.add_body_text(c1)
                self.file_position += 2
            elif c == '\\' and c1 == "'":
                function_info.add_body_text(c1)
                self.file_position += 2
            elif c == '"':
                self.file_position += 1
                if not inside_single_quotes:
                    inside_double_quotes = not inside_double_quotes
            elif c == '\\':
                self.file_position += 1
                if not inside_double_quotes:
                    inside_single_quotes = not inside_single_quotes
            elif c == "'" and c1 == '{':
                self.file_position += 2
            elif c == "'" and c1 == '}':
                function_info.add_body_text(c1)
                self.file_position += 2
            elif c == '{':
                self.file_position += 1
                if not inside_single_quotes and not inside_double_quotes:
                    bracket_count += 1
            elif c == '}':
                self.file_position += 1
                if not inside_single_quotes and not inside_double_quotes:
                    bracket_count -= 1
            elif c == '\n':
                inside_comment = False
                self.file_position += 1
                self.line_number += 1
            else:
                self.file_position += 1
            if bracket_count == 0:
                self._set_parser_state(Bparse.DATA_STATE)
                break

    def _skip_white_space(self):
        while not self.file_buffer.past_end_of_file():
            c = self.file_buffer[self.file_position]
            if c == '\r' and self.file_buffer[self.file_position + 1] == '\n':
                self.file_position += 2
                self.line_number += 1
            elif c == '\n':
                self.file_position += 1
                self.line_number += 1
            elif c.isspace():
                self.file_position += 1
            else:
                break

    def _set_copy_method_body(self,
                             copy_function_info,
                             data_member_type_and_name_info_list):
        copy_function_info.add_body_text('{\n')
        copy_function_info.add_body_text('    // xxxxxx - The code below does a shallow copy of the class data members.\n')
        copy_function_info.add_body_text('    // If any data members are pointers and a deep copy is needed then this code\n')
        copy_function_info.add_body_text('    // should be changed.\n')

        for data_member_type_and_name_info in data_member_type_and_name_info_list:
            # Don't copy static data members.
            the_type_info = data_member_type_and_name_info.get_type_info()
            if the_type_info.get_static_virtual_qualifier_type() != TypeInfo.STATIC_QUALIFIER_TYPE:
                name_text = data_member_type_and_name_info.get_name()
                assignment_line = '    {0} = that.{1};\n'.format(name_text, name_text)
                copy_function_info.add_body_text(assignment_line)
        copy_function_info.add_body_text('}')

    def _save_include_name(self,
                           definition_class_name_set,
                           implementation_class_name_set,
                           the_type_info):
        """ Save the type name in either the definition class name set or the
            implementation class name set.
        """
        include_name = the_type_info.get_name()
        if include_name and include_name != self.class_name and include_name != self.destructor_name:
            type_modifier = the_type_info.get_type_modifier()
            # A type such as "std::vector<ClassName>" can be broken into two types,
            # both "std::vector" and "ClassName". Call the __save_include_name() method
            # for each type.
            if '<' in include_name:
                include_name_list = include_name.split('<')
                include_name = include_name_list[0]
                include_name = self.file_name_manager.get_include_file_name(include_name)
                self._add_include_name(definition_class_name_set,
                                       implementation_class_name_set,
                                       type_modifier,
                                       include_name)
                if len(include_name_list) > 1:
                    include_name = include_name_list[1]
                    if include_name.endswith('>'):
                        include_name = include_name[:-1]
                    self._add_include_name(definition_class_name_set,
                                           implementation_class_name_set,
                                           type_modifier,
                                           include_name)
            else:
                self._add_include_name(definition_class_name_set,
                                       implementation_class_name_set,
                                       type_modifier,
                                       include_name)

    def _add_include_name(self,
                          definition_class_name_set,
                          implementation_class_name_set,
                          type_modifier,
                          include_name):
        #  If the string is not an intrinsic type then it is assumed
        #  to be a class name.
        if include_name and not self._is_intrinsic_type(include_name):
            # Save the definition class name set.
            if (type_modifier in ['&', '&*', '*', '**'] and include_name[0] != '<'):
                implementation_class_name_set.add(include_name)
            else:
                definition_class_name_set.add(include_name)
                # Because the type is explicitly needed in the class definition file,
                # The type can be removed from the 'implementation_class_name_set' container.
                if include_name in implementation_class_name_set:
                    implementation_class_name_set.remove(include_name)

    def get_input_file_line(self, line_number):
        input_line_number = 1
        start_of_line = 0
        end_of_line = 0
        file_position = 0
        while not self.file_buffer.past_end_of_file():
            c = self.file_buffer[file_position]
            if c == '\r' and self.file_buffer[file_position + 1] == '\n':
                file_position += 2
                input_line_number += 1
            elif c == '\n':
                file_position += 1
                input_line_number += 1
            else:
                file_position += 1
            # Has the line been found?
            if input_line_number == line_number - 1:
                start_of_line = file_position
            elif input_line_number == line_number + 1:
                end_of_line = file_position
                break
        if end_of_line == 0:
            end_of_line = file_position
        line_text = ''
        if end_of_line > start_of_line:
            for file_position in xrange(start_of_line, end_of_line + 1):
                cc = self.file_buffer[file_position]
                if cc != '\0':
                    line_text += cc
        return line_text

    def _is_intrinsic_type(self, name):
        return self.intrinsic_type_checker.is_intrinsic_type(name)

    def _current_parser_state(self):
        return self.parser_state
 
    def _set_parser_state(self, parser_state):
        self.parser_state = parser_state
