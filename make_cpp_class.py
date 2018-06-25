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
"""
This program makes it easier to produce a C++ class header file and
implementation file.  This program will often produce correct code,
however, the program cannot always identify the proper header files
to include, and therefore the generated code might have to be edited
before the code can be successfully compiled.  This program saves a lot
of typing.

The program is for experienced C++ programmers, because understanding the
changes that must be made to the generated code require understanding the
C++ language. 

    High Level usage

The program takes file as input and a class name and a few optional switch
arguments.  The input file contains code in a very simple language.  Once
code is generated using this program, the input file can be discarded.

The body of any method in the input file is copied to the generated code
without any changes.  In other words, you still must write the code that
does anything, the program merely eliminates the boilerplate that must
normally be written when producing a C++ class.

The program does relatively little lexical analysis of the data in the
input file.  While some sequences will be recognized as erroneous, if the
input file is not correct the program might produce garbage.  This is
another reason it's important to know C++ if you use this program.

Usage:

    python make_cpp_class.py <class_name> <input_file_name> [-b base_class_name] [-a author_name] [-f] [-t] 

    The program accepts the following switches:

        -b base_class_name, --base_class base_class_name  - Inherit from the named base class.
        -a author_name, --author author_name              - The author name.
        -f, --full                                        - Write full detailed header information.
        -t, --abstract                                    - Make all virtual methods be abstract methods.
        -h, --help                                        - Show help and exit

    The Input File format

    Data Member Format In The Input File

Data members are first in the file and are declared using the following
format:

    <Type> <Name> [= initial_value]<;>

The type can be a pointer parameter, a reference parameter, and be preceded
by const, volatile, or static.  'Const volatile", while valid, are not
allowed together.  I didn't implement this only to simplify the parser; if
needed use one keyword and add the other to the generated code.

A sample data member set might be:

short m_age;
int m_count = 7;
Foo_t * m_foo;
static const float m_height = 1.0;

If an initial value is supplied for a data member, then everything between
the equal sign and the terminating semicolon is used as the initial value
in the generated code.

Static data members generate the appropriate code in the header file and
implementation file.

    Constructors and the Destructor

After the data member declarations, the constructors, destructor, and methods
are listed in the input file.  Headers are written automatically for all
methods.

The return value for a method can be declared the same as for a data member
type and also allows the additional keywords 'inline' and 'virtual'.  These
cannot be used together and both should be first on the function declaration
line.

Because the class name is specified on the command line, when used for a
constructor or destructor, the class name is specified in the input file
using the character '@'.

Here are some examples that show two constructors and one virtual destructor.

@()
{
}

@(int x)
{
    // Some code here.
}

virtual ~@()
{
}

Member initialization lists are created for every constructor.  Member
initialization lists might need to be edited, but much of the time what
is written can be left as-is.

If the class name passed on the command line is 'Foobar' and the data
member list is the example shown above, then the first constructor
definition shown above, which starts with the '@' character, would
produce the following generated code:

Foobar::Foobar()
  : m_age(0),
  , m_count(7)
  , m_foo(NULL)
{
}

    The Copy Constructor and the Equals Operator

Putting the keyword, "copy:" on an input line will automatically generate
code for a copy constructor and code for the equals operator.  Both of
these methods will call a generated 'Copy' method that does a shallow copy
of the class data members.

Putting the keyword "nocopy:" on an input line will generate a 'private'
copy constructor and equals operator, both without any implementation,
thus instances of the class cannot be copied.

    Methods

Methods are declared similar to a C function, but the methods can be made
'const' by putting the 'const' keyword at the end.  Also, "= 0" can be added
to the end to make the method an abstract method.  If "= 0" is used, then no
method body will be generated in the class implementation file.  Here are
three method examples that could be specified in the input file:

double accumulate(double addend)
{
    m_sum += addend;
    return m_sum;
}

const & Foobar GetFoobar() const
{
    return m_foobar;
}

virtual int doSomething(int anIntegerToUseForSomething) const
{
    // Need to return something here, but make_cpp_class.py won't detect
    // that no value is returned as the function body is merely copied
    // into the method in the generated code.
}

A method can also be declared using the 'static' keyword.

    Property Methods

There is another special keyword to define properties.  A data member for
a property should 'not' be declared in the data member section mentioned
above.  The syntax to generate a property, which uses the "property:"
keyword is:

    property: <type> <data_member_name> <property_name>

This defintion will create a method named set<property_name> and a 'get' method named <property_name>.

Here is an example property definition.

    property: int m_age Age

The property definition above will result in the code generator writing the
following data member and methods.  (The code headers are omitted here for
brevity).

int m_age;

int Age() const
{
    return m_age;
}

void setAge(int the_value)
{
     m_age = the_value;
}

If the data type used in the declaration of a property is not an intrinsic
type, then the code generator will generate slightly different code than
shown above.  Here is an example:

    property: Person_t * m_person Person

Person_t * m_person;

Person_t Person() const
{
    return m_person;
}

void setPerson(const Person_t * the_value)
{
     m_person = the_value;
}

    The Message Body

The parser detects the start of a method body by parsing past the
method signature to the first open curly bracket character, or '{'.

At that point, ignoring brackets that are contained in string
declarations, an open curly bracket causes a counter that is initially
at zero to be incremented, and close curly brackets '}' causes the
counter to be decremented.  When the count returns to zero, the method
body is ended.

If the brackets are not correct in the input file, the program will
produce incorrect code.

    The Mistakes This Program Makes

As already mentioned, there is minimal lexical analysis of the input file,
so garbage in will result in garbage out.

Also, the program makes the assumption that all type names that designate
either non-intrinsic (non-built-in) types or are that are not one of the
special type names that are handled in the include-file-manager code, will
generate an 'include' statement to include a header file with the same names
as the type name followed by the extension ".h".  Of course, this often
won't be a valid header file name, and therefore it will often be necessary
to either delete the include-statement or change the name of the header
file in the include statement.

Also, any data types in the body of the code are not detected, and it might
be necessary to include header files in the generated code for these types.

    Tips and Tricks

If I have some data that I know the program will not generate, such as a
comment-block, or 'include statements', and I want these in the header
file, I will declare an inline function, such as:

inline void dummy()
{
#include "foobar.h"
#include "barfoo.h"
}
"""
import sys
import os
from bclass import create_cpp_class_files
from argparse import ArgumentParser

def create_folder_under_current_directory(folder_name):
    current_path = os.getcwd()
    new_path = os.path.join(current_path, folder_name)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return new_path

# Start of main program.
def main(argv=None):
    # Initialize the command line parser.
    parser = ArgumentParser(description='This program creates C++ class files.',
                            epilog='Copyright (c) 2013 William Hallahan.',
                            add_help=True,
                            argument_default=None, # Global argument default
                            usage=__doc__)
    parser.add_argument(action='store', dest='class_name', help='The class name.')
    parser.add_argument(action='store', dest='input_file_name', help='The input file name.')
    parser.add_argument('-b', '--base_class', action='store', dest='base_class', default='', help='Inherit from the named base class.')
    parser.add_argument('-a', '--author', action='store', dest='author', default='', help='The author name.')
    parser.add_argument('-f', '--full', action='store_true', dest='full_header', default=False, help='Write full detailed header information.')
    parser.add_argument('-t', '--abstract', action='store_true', dest='abstract_class', default=False, help='Create only abstract class header file.')
    # Parse the command line.
    arguments = parser.parse_args(args=argv)
    class_name = arguments.class_name
    input_file_name = arguments.input_file_name
    base_class = arguments.base_class
    author = arguments.author
    full_header = arguments.full_header
    abstract_class = arguments.abstract_class
    status = 0
    # Fully qualify the input file name by adding the current path.
    current_path = os.getcwd()
    input_file_name = os.path.join(current_path, input_file_name)
    # Create a 'class_name' folder.
    new_path = create_folder_under_current_directory(class_name)
    # Change the current working directory to the new folder.
    os.chdir(new_path)
    try:
       create_cpp_class_files(input_file_name,
                              class_name,
                              base_class,
                              author,
                              full_header,
                              abstract_class)
    except ValueError as value_error:
        print value_error
        status = -1
    except EnvironmentError as environment_error:
        print environment_error
        status = -1
    return status

if __name__ == "__main__":
    sys.exit(main())
