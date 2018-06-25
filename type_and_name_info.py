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

class TypeAndNameInfo:

    RENDER_NO_VALUE = 0
    RENDER_VALUE = 1

    def __init__(self):
        self.the_type_info = TypeInfo()
        self.name = ''
        self.value = ''

    def get_type_info(self):
        return self.the_type_info

    def set_type_info(self, value):
        a = value.get_static_virtual_qualifier_type()
        self.the_type_info.set_static_virtual_qualifier_type(a)
        b = value.get_const_volatile_qualifier_type()
        self.the_type_info.set_const_volatile_qualifier_type(b)
        c = value.get_name()
        self.the_type_info.set_name(c)
        d = value.get_type_modifier()
        self.the_type_info.set_type_modifier(d)

    def get_name(self):
        return self.name

    def set_name(self, value):
        value = value.strip()
        self.name = value

    def get_value(self):
        return self.value

    def set_value(self, value):
        value = value.strip()
        self.value = value

    def get_type_and_name_text(self,
                               render_type,
                               render_value):
        type_and_name_text = self.the_type_info.get_type_text(render_type)
        type_and_name_text = '{0} {1}'.format(type_and_name_text, self.name)
        if self.value and render_value == (TypeAndNameInfo.RENDER_VALUE):
            type_and_name_text = '{0} = {1}'.format(type_and_name_text, self.value)
        return type_and_name_text

    def clear(self):
        self.the_type_info = None
        self.name = ''
        self.value = ''
