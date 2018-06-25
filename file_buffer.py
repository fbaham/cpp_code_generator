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

class FileBuffer:

    def __init__(self, input_file):
        self.file_buffer_text = input_file.read()
        self.input_file = input_file
        self.end_of_file = False

    def past_end_of_file(self):
        return self.end_of_file

    def get_file_size(self):
        return len(self.file_buffer_text)

    def __getitem__(self, index):
        self.end_of_file = False
        c = chr(0)
        if 0 <= index < len(self.file_buffer_text):
            c = self.file_buffer_text[index]
        else:
            self.end_of_file = True
        return c
