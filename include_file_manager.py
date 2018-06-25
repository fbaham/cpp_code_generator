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
  The following standard IO types are supported:

    std::cout
    std::cin
    std::ifstream
    std::ofstream

  The following STL library types are supported:

    std::string
    std::basic_string
    std::list
    std::vector
    std::deque
    std::set
    std::multiset
    std::map
    std::multimap
    std::queue
    std::stack
    std::exception

  The following boost library types are supported:

    boost::shared_ptr
    boost::shared_array
    boost::intrusive_ptr
    boost::scoped_ptr
    boost::weak_ptr
    boost::mutex
    boost::try_mutex
    boost::shared_mutex
    boost::recursive_mutex
    boost::thread
    boost::condition
    boost::bimaps::bimap
    boost::bimaps::set_of
    boost::circular_buffer
    boost::date_time
    boost::timer
    boost::int8_t
    boost::uint8_t
    boost::int16_t
    boost::uint16_t
    boost::int32_t
    boost::uint32_t
    boost::int64_t
    boost::uint64_t
"""

class IncludeFileManager:

    def __init__(self):
        self.file_name_dict = {'std::cout' : '<iostream>',
                               'std::cin' : '<iostream>',
                               'std::ifstream' : '<fstream>',
                               'std::ofstream' : '<fstream>',
                               'std::string' : '<string>',
                               'std::basic_string' : '<string>',
                               'std::list' : '<list>',
                               'std::vector' : '<vector>',
                               'std::deque' : '<deque>',
                               'std::set' : '<set>',
                               'std::multiset' : '<multiset>',
                               'std::map' : '<map>',
                               'std::multimap' : '<multimap>',
                               'std::queue' : '<queue>',
                               'std::stack' : '<stack>',
                               'std::exception' : '<exception>',
                               'boost::shared_ptr' : '<boost/shared_ptr->hpp>',
                               'boost::shared_array' : '<boost/shared_array.hpp>',
                               'boost::intrusive_ptr' : '<boost/intrusive_ptr->hpp>',
                               'boost::scoped_ptr' : '<boost/scoped_ptr->hpp>',
                               'boost::weak_ptr' : '<boost/weak_ptr->hpp>',
                               'boost::mutex' : '<boost/thread/mutex.hpp>',
                               'boost::try_mutex' : '<boost/thread/mutex.hpp>',
                               'boost::shared_mutex' : '<boost/thread/shared_mutex.hpp>',
                               'boost::recursive_mutex' : '<boost/thread/recursive_mutex.hpp>',
                               'boost::thread' : '<boost/thread/thread.hpp>',
                               'boost::condition' : '<boost/thread/condition.hpp>',
                               'boost::bimaps::bimap' : '<boost/bimap/bimap.hpp>',
                               'boost::bimaps::set_of' : '<boost/bimap/set_of.hpp>',
                               'boost::circular_buffer' : '<boost/circular_buffer.hpp>',
                               'boost::date_time' : '<boost/date_time.hpp>',
                               'boost::timer' : '<boost/timer.hpp>',
                               'boost::int8_t' : '<boost/cstdint.hpp>',
                               'boost::uint8_t' : '<boost/cstdint.hpp>',
                               'boost::int16_t' : '<boost/cstdint.hpp>',
                               'boost::uint16_t' : '<boost/cstdint.hpp>',
                               'boost::int32_t' : '<boost/cstdint.hpp>',
                               'boost::uint32_t' : '<boost/cstdint.hpp>',
                               'boost::int64_t' : '<boost/cstdint.hpp>',
                               'boost::uint64_t' : '<boost/cstdint.hpp>'}

    def get_include_file_name(self, type_name):
        file_name = type_name
        if type_name in self.file_name_dict:
            file_name = self.file_name_dict[type_name]
        return file_name
