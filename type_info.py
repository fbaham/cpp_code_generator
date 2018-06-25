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

class TypeInfo:

    # static-virtual type declarations
    NORMAL_QUALIFIER_TYPE = 0
    STATIC_QUALIFIER_TYPE = 1
    VIRTUAL_QUALIFIER_TYPE = 2

    # const-volatile type declarations
    NORMAL_QUALIFIER_TYPE = 0
    CONST_QUALIFIER_TYPE = 1
    VOLATILE_QUALIFIER_TYPE = 2

    # Constants to determine how this TypeInfo instance is rendered.
    RENDER_DEFINITION_DATA_TYPE = 0
    RENDER_DEFINITION_METHOD_RETURN_TYPE = 1
    RENDER_IMPLEMENTATION_OR_ARGUMENT_TYPE = 2

    def __init__(self):
        self.static_virtual_qualifier_type = ''
        self.const_volatile_qualifier_type = ''
        self.type_name = ''
        self.type_modifier_text = ''
        self.intrinsic_type_list = ['signed', 'unsigned', 'char', 'signed char', 'unsigned char', 'wchar_t',
                                    'short', 'signed short' 'unsigned short', 'int', 'signed int', 'unsigned int',
                                    'long', 'signed long', 'unsigned long', '__int64', 'signed __int64', 'unsigned __int64',
                                    'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64',
                                    'int8_t', 'int16_t', 'int32_t', 'int64_t', 'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
                                    'float',  'double', 'bool', 'void', 'BOOL', 'VOID', 'TCHAR', 'BYTE', 'WORD', 'DWORD',
                                    'LPVOID', 'LPTCHAR', 'LPBYTE', 'LPWORD', 'LPDWORD', 'BYTE_PTR', 'WORD_PTR', 'INT_PTR',
                                    'UINT_PTR', 'DWORD_PTR']

    def get_static_virtual_qualifier_type(self):
        return self.static_virtual_qualifier_type

    def set_static_virtual_qualifier_type(self, value):
        self.static_virtual_qualifier_type = value

    def get_const_volatile_qualifier_type(self):
        return self.const_volatile_qualifier_type

    def set_const_volatile_qualifier_type(self, value):
        self.const_volatile_qualifier_type = value

    def get_name(self):
        return self.type_name

    def set_name(self, value):
        value = value.strip()
        self.type_name = value

    def get_type_modifier(self):
        return self.type_modifier_text

    def set_type_modifier(self, value):
        value = value.strip()
        self.type_modifier_text = value

    def get_type_text(self, render_type):
        type_text = ''
        if (render_type == TypeInfo.RENDER_DEFINITION_DATA_TYPE
            or render_type == TypeInfo.RENDER_DEFINITION_METHOD_RETURN_TYPE):
            # Add the static_virtual_qualifier type string.
            if self.static_virtual_qualifier_type == TypeInfo.STATIC_QUALIFIER_TYPE:
                type_text = 'static '
            elif self.static_virtual_qualifier_type == TypeInfo.VIRTUAL_QUALIFIER_TYPE:
                type_text = 'virtual '
        # Add the const_volatile_qualifier type string.
        if self.const_volatile_qualifier_type == TypeInfo.CONST_QUALIFIER_TYPE:
            type_text = '{0}const '.format(type_text)
        elif self.const_volatile_qualifier_type == TypeInfo.VOLATILE_QUALIFIER_TYPE:
            type_text = '{0}volatile '.format(type_text)
        # Add the type name.
        type_text = '{0}{1}'.format(type_text, self.type_name)
        # Add type modifier text.
        if self.type_modifier_text:
            type_text = '{0} {1}'.format(type_text, self.type_modifier_text)
        return type_text

    def clear(self):
        self.static_virtual_qualifier_type = ''
        self.const_volatile_qualifier_type = ''
        self.type_name = ''
        self.type_modifier_text = ''

    def is_intrinsic_type(self, name):
        return name in self.intrinsic_type_list
