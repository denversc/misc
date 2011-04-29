################################################################################
# bigfiles.py
# By: Denver Coneybeare
# April 28, 2011
#
# Searches through the filesystem for files with the biggest size.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
Searches the filesystem for the biggest files.
"""

from __future__ import absolute_import
from __future__ import print_function

import argparse
import bisect
import collections
import glob
import itertools
import os
import sys

################################################################################

class BigFilesArgumentParser(argparse.ArgumentParser):
    """
    The command-line arguments parser for this application.
    """

    def __init__(self, prog=None):
        prog = prog if prog is not None else os.path.basename(sys.argv[0])
        argparse.ArgumentParser.__init__(self,
            description=__doc__,
            prog=prog,
        )

        self.add_argument(
            "paths",
            type=self.type_path_wildcard,
            nargs="*",
            help="The paths of the files and/or directories to search; " +
                "May contain wildcard characters '*' and '?';" +
                "if none are specified then the current directory is used"
        )

        self.add_argument(
            "-n", "--num-results",
            type=self.type_positive_integer,
            default=30,
            help="The maximum number of results to print (default %(default)i)"
        )

        self.add_argument(
            "-i", "--invert",
            action="store_true",
            default=False,
            help="If specified, show the smallest files instead of the largest"
        )

        self.add_argument(
            "-r", "--reverse-order",
            action="store_true",
            default=False,
            help="If specified, list the results in reverse order"
        )

        self.add_argument(
            "-e", "--ignore-errors",
            action="store_true",
            default=False,
            help="If specified, ignore errors accessing files"
        )

        self.add_argument(
            "-p", "--no-padding",
            action="store_true",
            default=False,
            help="If specified, do not left-pad file sizes in output"
        )

        self.add_argument(
            "-f", "--format-sizes",
            action="store_true",
            default=False,
            help="If specified, format the file sizes into a human-readable " +
                "format (eg. 500kb instead of 500000); these values are base 10"
        )

        self.add_argument(
            "-b", "--binary-sizes",
            action="store_true",
            default=False,
            help="If specified with --format-sizes, sizes will be formatted " +
                "using base 2 units instead of base 10"
        )

    def parse_args(self, *args, **kwargs):
        """
        Parses the command-line arguments.
        This method simply calls the method with the same name in the superclass
        with the given parameters, and then tweaks the return value.
        """
        result = argparse.ArgumentParser.parse_args(self, *args, **kwargs)
        if len(result.paths) == 0:
            paths = self.type_path_wildcard("*")
            result.paths.append(paths)
        return result

    @staticmethod
    def type_positive_integer(value):
        """
        Converts a string to an integer.
        The *value* parameter must be a string and will be converted to an
        integer using the built-in int() function.
        If the conversion fails or if the resulting integer is less than zero
        then argparse.ArgumentTypeError is raised.
        Returns the integer to which the given value was converted.
        """
        try:
            value_int = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("invalid integer: %s" % value)

        if value_int < 0:
            raise argparse.ArgumentTypeError("invalid value: %s" % value)

        return value_int

    @staticmethod
    def type_path_wildcard(value):
        """
        Converts a string to an iterable of paths matched by the wildcard
        pattern of the given string.
        The *value* parameter must be a string and will be converted to an
        iterable using the glob.glob() function.
        If the given pattern matches zero files or directories then
        argparse.ArgumentTypeError is raised.
        Returns an iterator over the matching paths.
        """
        # convert the pattern to a list of paths, failing if zero matches
        paths = glob.iglob(value)
        try:
            first_path = next(paths)
        except StopIteration:
            raise argparse.ArgumentTypeError("file/directory not found: %s" %
                value)

        return itertools.chain([first_path], paths)

################################################################################

class BigFilesSearchEngine(object):
    """
    Searches a set of paths for the largest files.
    """

    def __init__(self, max_results, size_cmp):
        self.max_results = max_results
        self.size_cmp = size_cmp
        self.sizes = []
        self.paths = []

    def add_file(self, path):
        """
        Updates this object by searching the file with the given path.
        The *path* parameter must be the string whose value is the path of a
        file whose size to update this search engine with.
        Raises OSError if an error occurs retrieving the size of the file.
        This method simply determines the size of the given file and then
        invokes self.add_file_info() with the given path and the size of the
        file.
        """
        stat_info = os.stat(path)
        size = stat_info.st_size
        self.add_file_info(path, size)

    def add_file_info(self, path, size):
        """
        Updates this object by searching the file with the given path.
        The *path* parameter must be the string whose value is the path of a
        file whose size to update this search engine with.
        The *size* parameter must be an integer whose value is the size of the
        given file.
        """
        if len(self.sizes) < self.max_results or \
                self.size_cmp(size, self.sizes[0]) > 0:

            index = bisect.bisect_left(self.sizes, size)
            self.sizes.insert(index, size)
            self.paths.insert(index, path)

            if len(self.sizes) > self.max_results:
                del self.sizes[0]
                del self.paths[0]


    def results(self):
        """
        Returns the results of the search.
        Returns an iterable that yields (size, path) tuples where *path* is
        a string whose value is the path of the file and *size* is an integer
        whose value is the size of the size of the file. 
        """
        return itertools.izip(self.sizes, self.paths)

################################################################################

def iter_paths(path):
    """
    Walks recursively through all files in a path.
    The *path* parameter must be a string whose value is the path of a file or
    directory in the filesystem.
    Returns an iterable over a set of strings.
    If the given path is a file then that string is the only element yielded by
    the returned iterator.
    Otherwise, the given path is walked, recursively, and all discovered files
    have their paths yielded by the returned iterator.
    """
    if os.path.isdir(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                cur_path = os.path.join(dirpath, filename)
                yield cur_path
    else:
        yield path

################################################################################

UnitEntry = collections.namedtuple("UnitEntry", "size, name")

# Tables created from http://en.wikipedia.org/wiki/Template:Quantities_of_bytes

UNIT_TABLE_SI_DECIMAL = (
    UnitEntry(10 ** 24, "YB"),
    UnitEntry(10 ** 21, "ZB"),
    UnitEntry(10 ** 18, "EB"),
    UnitEntry(10 ** 15, "PB"),
    UnitEntry(10 ** 12, "TB"),
    UnitEntry(10 ** 9, "GB"),
    UnitEntry(10 ** 6, "MB"),
    UnitEntry(10 ** 3, "kB"),
)

UNIT_TABLE_IEC_BINARY = (
    UnitEntry(2 ** 80, "YiB"),
    UnitEntry(2 ** 70, "ZiB"),
    UnitEntry(2 ** 60, "EiB"),
    UnitEntry(2 ** 50, "PiB"),
    UnitEntry(2 ** 40, "TiB"),
    UnitEntry(2 ** 30, "GiB"),
    UnitEntry(2 ** 20, "MiB"),
    UnitEntry(2 ** 10, "KiB"),
)

def format_file_size(size, table):
    """
    Converts a size to a human-readable string.
    The *size* parameter must be an integer to convert.
    The *table* parameter must be a tuple; TABLE_SI_DECIMAL and TABLE_IEC_BINARY
    are two examples of tables.
    Returns a string whose value is the given size converted to a string that
    is more human readable, such as 1.25kb instead of 125000.
    """
    unit = None
    for unit in table:
        if size > unit.size:
            break

    value = float(size) / float(unit.size)
    return "{size:.2f}{name}".format(size=value, name=unit.name)

################################################################################

def main(args):
    """
    The main method for this application.
    The *args* parameter must be an iterable of strings whose values are the
    command-line arguments.
    Returns an integer whose value is the exit code: 0 on success, 1 on failure,
    2 on invalid command-line arguments.
    """

    # parse the command-line arguments
    args = tuple(args)
    args_parser = BigFilesArgumentParser()
    settings = args_parser.parse_args(args=args)

    # setup the search engine
    size_cmp = cmp if not settings.invert else lambda x, y:-cmp(x, y)
    search = BigFilesSearchEngine(
        max_results=settings.num_results,
        size_cmp=size_cmp,
    )

    # search the files specified by the user
    for path_lists in settings.paths:
        for paths in path_lists:
            for path in iter_paths(paths):
                try:
                    search.add_file(path)
                except OSError as e:
                    if settings.ignore_errors:
                        continue
                    print("ERROR: unable to process file: %s (%s)" %
                        (path, e.strerror))
                    return 1

    # print the search results (if there are any)
    results = list(search.results())
    if len(results) > 0:

        if settings.format_sizes:
            unit_table = UNIT_TABLE_IEC_BINARY if settings.binary_sizes \
                else UNIT_TABLE_SI_DECIMAL
            size_formatter = lambda x: format_file_size(x, unit_table)
        else:
            size_formatter = str

        if settings.no_padding:
            max_size_str_len = 0
        else:
            max_size_str_len = max(len(size_formatter(x[0])) for x in results)

        output_template = "{size:>" + str(max_size_str_len) + "} {path}"

        if settings.invert == settings.reverse_order:
            results.reverse()

        for (size, path) in results:
            size_str = size_formatter(size)
            formatted_line = output_template.format(size=size_str, path=path)
            print(formatted_line)

    return 0

################################################################################
# Main Entry Point
################################################################################

if __name__ == "__main__":
    try:
        exit_code = main(sys.argv[1:])
    except KeyboardInterrupt:
        print("ERROR: Application terminated by keyboard interrupt",
            file=sys.stderr)
        exit_code = 1
    sys.exit(exit_code)
