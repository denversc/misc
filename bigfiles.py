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

import argparse
import bisect
import collections
import glob
import itertools
import os
import sqlite3
import sys

################################################################################

def log(x, base):
    """
    Computes the logarithm of the given value in the given base.
    The *x* and *base* parameters must both be integers and the return value
    is also an integer.
    The given *x* must be a perfect power of *base* or else ValueError is
    raised.
    """
    if x < 0:
        raise ValueError("invalid x: %i" % x)
    elif x == 1:
        return 0

    exponent = 1
    while True:
        power = base ** exponent
        if power == x:
            return exponent
        elif power > x:
            raise ValueError("%i is not a perfect power of %i" % (x, base))
        exponent += 1

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
                "May contain wildcard characters '*' and '?'; " +
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
            help="Show the smallest files instead of the largest"
        )

        self.add_argument(
            "-r", "--reverse-order",
            action="store_true",
            default=False,
            help="List the results in reverse order"
        )

        self.add_argument(
            "-e", "--ignore-errors",
            action="store_true",
            default=False,
            help="Ignore errors accessing files"
        )

        # Arguments for size formatting

        self.add_argument(
            "-p", "--no-padding",
            action="store_true",
            default=False,
            help="Do not left-pad file sizes in output"
        )

        self.add_argument(
            "-f", "--format-sizes",
            action="store_true",
            default=False,
            help="Format the file sizes into a human-readable " +
                "format (eg. 500kB instead of 500000); these values are base 10"
        )

        self.add_argument(
            "-b", "--binary-sizes",
            action="store_true",
            default=False,
            help="Causes size formatting done by --format-sizes to use IEC " +
                "Binary base 2 units instead of SI Decimal base 10"
        )

        class ListSizeUnitsAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                parser.list_sizes()
                parser.exit(0)

        self.add_argument(
            "--list-size-units",
            action=ListSizeUnitsAction,
            nargs=0,
            help="List the units of size used by --format-sizes"
        )

        # Arguments for databases

        self.add_argument(
            "--save",
            dest="db_save_path",
            help="Save the paths and file sizes of all visited files into " +
                "an SQLite database with the given name"
        )

        self.add_argument(
            "--load",
            type=self.type_file_exists,
            dest="db_load_path",
            help="Load paths and file sizes from this file, which must be " +
                "an SQLite database created with --save, in addition to " +
                "the paths specified in the positional parameters"
        )

    def parse_args(self, *args, **kwargs):
        """
        Parses the command-line arguments.
        This method simply calls the method with the same name in the superclass
        with the given parameters, and then tweaks the return value.
        """
        result = argparse.ArgumentParser.parse_args(self, *args, **kwargs)
        if len(result.paths) == 0 and result.db_load_path is None:
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

    @staticmethod
    def type_file_exists(value):
        """
        Argument type is an existing file.
        The *value* parameter must be a string whose value to validate.
        If the path of the given value does not exist or is not a file then
        argparse.ArgumentTypeError is raised.
        Returns the given string verbatim.
        """
        if not os.path.exists(value):
            raise argparse.ArgumentTypeError("file not found: %s" % value)
        elif not os.path.isfile(value):
            raise argparse.ArgumentTypeError("not a file: %s" % value)
        return value

    @classmethod
    def list_sizes(cls):
        """
        Prints lines to standard output about the different units that are
        displayed by --format-sizes.  Uses list_sizes_for_type() to print the
        different unit tables.
        """
        cls.list_sizes_for_type("SI Decimal", UNIT_TABLE_SI_DECIMAL, 10)
        print()
        cls.list_sizes_for_type("IEC Binary", UNIT_TABLE_IEC_BINARY, 2)

    @staticmethod
    def list_sizes_for_type(name, unit_table, base):
        """
        Prints the unit table for the given units to standard output.
        The *name* parameter must be a string whose value is the name of the
        units whose table to print.
        The *unit_table* parameter must be a unit table; predefined unit tables
        are UNIT_TABLE_SI_DECIMAL and UNIT_TABLE_IEC_BINARY.
        The *base* parameter must be an integer that is the exponential base
        of all sizes of the given unit.
        """
        title = "%s Units" % name
        print(title)
        print("=" * len(title))
        print()

        unit_table = list(unit_table)
        unit_table.reverse()
        for unit in unit_table:
            exp = int(log(unit.size, base))
            print("1 {name} = {base:d}^{exp:d} {size:,d} bytes".format(
                name=unit.name, size=unit.size, base=base, exp=exp))

################################################################################

class BigFilesSearchEngine(object):
    """
    Searches a set of paths for the largest files.
    """

    def __init__(self, max_results, invert):
        self.max_results = max_results
        self.invert = invert
        self.sizes = []
        self.paths = []

    def add_file(self, path, size):
        """
        Updates this object by searching the file with the given path.
        The *path* parameter must be the string whose value is the path of a
        file whose size to update this search engine with.
        The *size* parameter must be an integer whose value is the size of the
        given file.
        """
        if len(self.sizes) < self.max_results or \
                self.cmp_sizes(size, self.sizes[0]) > 0:

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
        return zip(self.sizes, self.paths)

    def cmp_sizes(self, size1, size2):
        """
        Compares two sizes for relative ordering.
        The "size1" and "size2" parameters must both be integers.
        If size1 is greater than, less than, or equal to size2 then a value
        greater than zero, less than zero, or equal to zero will be returned,
        respectively.
        The return values are inverted if self.inverted evaluates to True.
        """
        difference = size1 - size2
        if self.invert:
            difference = -difference
        return difference

################################################################################

class Database(object):

    def __init__(self, path):
        self.path = path
        self.con = sqlite3.connect(path)

    def initialize(self):
        """
        Initializes this connection and prepares it for use.
        This method sets up the connection and creates any required tables.
        """
        cur = self.con.cursor()

        # set some pragmas to increase performance
        cur.execute("PRAGMA fullfsync = off")
        cur.execute("PRAGMA journal_mode = off")
        cur.execute("PRAGMA synchronous = off")

        # create the table if it does not already exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS files (
                path TEXT,
                size INTEGER
            )
        """)

        self.commit()

    def close(self):
        """
        Closes this connection from use.
        """
        self.con.close()

    def commit(self):
        """
        Commits all changes since the last commit.
        """
        self.con.commit()

    def add_file(self, path, size):
        """
        Adds a file with the given path and size.
        The *path* parameter must be the string whose value is the path of a
        file whose size to update this search engine with.
        The *size* parameter must be an integer whose value is the size of the
        given file.
        """
        self.con.execute("INSERT INTO files (path, size) VALUES (?, ?)",
            (path, size))

    def __iter__(self):
        """
        Returns an iterator over the files and sizes in the database.
        Returns (size, path) tuples where *path* is a string whose value is the
        path of a file in the filesystem and *size* is an integer whose value is
        the size of that file.  Raises sqlite3.Error on error.
        """
        cur = self.con.cursor()
        cur.execute("SELECT size, path FROM files")
        for result in cur:
            yield result

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
    is more human readable, such as 1.25kB instead of 125000.
    """
    unit = None
    for unit in table:
        if size > unit.size:
            break

    value = float(size) / float(unit.size)
    return "{size:.2f}{name}".format(size=value, name=unit.name)

################################################################################

def print_results(search, format_size_units, no_padding, reverse_order):
    """
    Prints search results to standard output.
    *search* must be an instance of BigFilesSearchEngine whose results to print.
    *format_size_units* is the unit table used to format sizes for output; if
    None then the integer sizes will be printed without formatting; the
    predefined units are UNIT_TABLE_SI_DECIMAL and UNIT_TABLE_IEC_BINARY.
    If *no_padding* evaluates to True, then the left padding of the sizes is
    not done.
    If *reverse* evaluates to True, then the order in which the search results
    are printed is reversed.
    """

    results = list(search.results())
    if reverse_order:
        results.reverse()

    if format_size_units is not None:
        size_formatter = lambda x: format_file_size(x, format_size_units)
    else:
        size_formatter = str

    if no_padding or len(results) == 0:
        max_size_str_len = 0
    else:
        max_size_str_len = max(len(size_formatter(x[0])) for x in results)

    output_template = "{size:>" + str(max_size_str_len) + "} {path}"

    for (size, path) in results:
        size_str = size_formatter(size)
        formatted_line = output_template.format(size=size_str, path=path)
        print(formatted_line)

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

    search_engines = []

    # setup the search engine
    search = BigFilesSearchEngine(
        max_results=settings.num_results,
        invert=settings.invert,
    )
    search_engines.append(search)

    # setup the database, if specified
    if settings.db_save_path is not None:
        save_db = Database(settings.db_save_path)
        search_engines.append(save_db)
    else:
        save_db = None

    # search the files specified by the user
    try:
        if save_db is not None:
            try:
                save_db.initialize()
            except sqlite3.Error as e:
                print("ERROR: unable to initialize sqlite database: %s (%s)" %
                    (save_db.path, e))
                return 1

        for path_lists in settings.paths:
            for paths in path_lists:
                for path in iter_paths(paths):
                    try:
                        stat_info = os.stat(path)
                    except OSError as e:
                        if settings.ignore_errors:
                            continue
                        print("ERROR: unable to process file: %s (%s)" %
                            (path, e.strerror))
                        return 1

                    size = stat_info.st_size
                    for search_engine in search_engines:
                        search_engine.add_file(path, size)

        if settings.db_load_path is not None:
            load_db = Database(settings.db_load_path)
            try:
                try:
                    load_db.initialize()
                except sqlite3.Error as e:
                    print("ERROR: unable to initialize sqlite database: %s (%s)"
                        % (load_db.path, e))
                    return 1
                for (size, path) in load_db:
                    for search_engine in search_engines:
                        search_engine.add_file(path, size)
            finally:
                load_db.close()

    finally:
        if save_db is not None:
            try:
                save_db.commit()
            finally:
                save_db.close()

    # print the results
    if not settings.format_sizes:
        format_size_units = None
    elif settings.binary_sizes:
        format_size_units = UNIT_TABLE_IEC_BINARY
    else:
        format_size_units = UNIT_TABLE_SI_DECIMAL

    print_results(
        search=search,
        format_size_units=format_size_units,
        no_padding=settings.no_padding,
        reverse_order=(settings.invert == settings.reverse_order),
    )

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
