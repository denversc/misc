#!/usr/bin/python

from __future__ import print_function

import atexit
import argparse
import os
import sqlite3
import sys
import tempfile

####################################################################################################

DESCRIPTION = \
"""
Reads a text file line-by-line and counts how many times each line occurs.  The topmost frequent
or infrequent are printed after the file is read.
"""

####################################################################################################

class GeneralException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

####################################################################################################

class ArgumentParseException(Exception):
    def __init__(self, exit_code, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.exit_code = exit_code

####################################################################################################

def parse_args(args=None):
    """
    Parses the command-line arguments for this application.  The given "args" must be an iterable
    of strings whose values are the arguments to parse; if None, uses sys.argv[1:].  Returns a new
    Settings object with the parsed values.  Raises ArgumentParseException if parsing fails or if the
    application should simply exit as if successful.  In the latter case the exit_code attribute
    will be equal to zero; otherwise, it should exit with the given exit code.
    """

    class MyArgumentParser(argparse.ArgumentParser):
        def __init__(self, *args, **kwargs):
            argparse.ArgumentParser.__init__(self, *args, **kwargs)
        def exit(self, status=0, message=None):
            raise ArgumentParseException(status, message)
        def error(self, message):
            self.exit(status=2, message=message)
    
    def file_arg(path):
        if not os.path.exists(path):
            raise argparse.ArgumentTypeError("file not found: %s" % path)
        elif not os.path.isfile(path):
            raise argparse.ArgumentTypeError("not a file: %s" % path)
        return path

    parser = MyArgumentParser(
        description=DESCRIPTION,
        add_help=True,
    )

    parser.add_argument(
        "files",
        type=file_arg,
        nargs="*",
        help="The list of files to read and whose frequency to print.  If none are specified " +
            "the standard input is read.",
    )

    parser.add_argument(
        "-n",
        type=int,
        default=10,
        help="The top number of lines to print.  If 0 (zero) then print the count of all lines. " +
            "If less than zero, print the least frequent lines instead of the most frequent.  " +
            "Default: %(default)i",
    )

    parser.add_argument(
        "-e", "--include-empty-lines",
        action="store_true",
        default=False,
        help="If specified, include empty lines in the output.  By default, empty lines are " +
            "ignored",
    )

    parser.add_argument(
        "-t", "--trim",
        action="store_true",
        default=False,
        help="If specified, trim leading and trailing whitespace from lines",
    )

    parser.add_argument(
        "-d", "--disk",
        action="store_const",
        default=None,
        const=create_temp_file(),
        dest="db_path",
        help="If specified, store the internal database into a temporary file intead of in " +
            "memory; this decreases performance but may fix out-of-memory errors",
    )

    parser.add_argument(
        "-a", "--all",
        action="store_const",
        const=0,
        dest="n",
        help="Shorthand for \"-n 0\"",
    )

    return parser.parse_args(args)

####################################################################################################

class LineFilter(object):
    def __init__(self, trim, include_empty):
        self.trim = trim
        self.include_empty = include_empty

    def __call__(self, s):
        if self.trim:
            s = s.strip()

        if not self.include_empty and len(s) == 0:
            s = None

        return s

####################################################################################################

class FreqDb(object):
    def __init__(self, path):
        self.path = path

    def open(self):
        if self.path is not None:
            db_path = self.path
        else:
            db_path = ":memory:"

        self.db = sqlite3.connect(db_path)
        self.db.text_factory = str
        
        # make it faster sine we don't really care about stability of the data
        cur = self.db.cursor()
        cur.execute("PRAGMA journal_mode = OFF")
        cur.execute("PRAGMA synchronous = OFF")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS freq (
                line TEXT PRIMARY KEY NOT NULL,
                count INTEGER NOT NULL
            )
            """
        )

        self.db.commit()

    def commit(self):
        self.db.commit()

    def close(self):
        try:
            self.db.close()
        finally:
            del self.db

    def inc(self, line):
        cur = self.db.cursor()

        cur.execute(
            """
            UPDATE freq
            SET count=count+1
            WHERE line=?
            """,
            (line,)
        )
        
        if cur.rowcount == 0:
            cur.execute(
                """
                INSERT INTO freq
                (line, count)
                VALUES
                (?, ?)
                """,
                (line, 1)
            )
    
    def top(self, n):        
        ordering = "DESC" if n >= 0 else "ASC"
        if n > 0:
            limit = n
        elif n < 0:
            limit = -n
        else:
            # according to sqlite docs, "If the LIMIT expression evaluates to a negative value, then
            # there is no upper bound on the number of rows returned
            limit = -1

        cur = self.db.cursor()
        cur.execute(
            """
            SELECT line, count
            FROM freq
            ORDER BY count %s
            LIMIT %i
            """
            % (ordering, limit)
        )

        while True:
            row = cur.fetchone()
            if row is None:
                break
            yield (row[0], row[1])

####################################################################################################

def iter_paths(paths):
    """
    A generator that returns the paths of files to read from a given list.  The "paths" parameter
    must be an iterable of strings whose values are the paths of the files to read.  If the list is
    empty then this generator only generates one value: None.  Otherwise, it generates each string
    from the given iterable in that order.
    """
    path_found = False
    for path in paths:
        yield path
        path_found = True

    if not path_found:
        yield None

####################################################################################################

def open_file(path):
    """
    Opens a file for reading in text mode.  The "path" parameter must be a string whose value is the
    path of the file to open; if None then sys.stdin is returned as the file.  Returns the tuple
    (f, close_enabled) where "f" is an open file object and "close_enabled" is a boolean that
    indicates whether or not the caller is responsible for closing the file object.  Raises
    GeneralException on error.
    """
    if path is None:
        f = sys.stdin
        close_enabled = False
    else:
        close_enabled = True
        try:
            f = open(path, "rt")
        except IOError as e:
            raise GeneralException("unable to open file for reading: %s (%s)" %
                (path, e.strerror))

    return (f, close_enabled)

####################################################################################################

def safe_delete(path):
    """
    Attempts to delete a file, printing a warning message to stderr on failure.  The "path"
    parameter must be a string whose value is the path of the file to delete.
    """
    try:
        os.unlink(path)
    except (OSError, IOError) as e:
        print("WARNING: unable to delete file: %s (%s)" % (path, e.strerror))

####################################################################################################

def create_temp_file():
    """
    Creates a temporary file that will be automatically deleted when this script exits.  Returns a
    string whose value is the path to the newly-created temporary file.
    """
    (handle, path) = tempfile.mkstemp()
    atexit.register(safe_delete, path)
    os.close(handle)
    return path

####################################################################################################

def freq_path(path, results, line_filter):
    """
    Reads a file for storing the frequency of line occurrences.  The "path" parameter must be a
    string whose value is the path of the file to open.  If an error occurs opening or reading from
    this file then GeneralException is raised.  The "results" parameter must be a dict; each line
    read from the given file will be put in the dict with the value 1; if the line is already a
    key then its value will be incremented by 1.  The "line_filter" parameter must be a function
    that will be specified each line as a string; if it returns None then the line will be
    discarded; otherwise, the returned string will be used as the line's value; may be None to
    perform no filtering.
    """
    (f, close_enabled) = open_file(path)
    try:
        for line in f:
            if line_filter is not None:
                line = line_filter(line)

            if line is not None:
                results.inc(line)
    finally:
        if close_enabled:
            f.close()

    results.commit()

####################################################################################################

def strip_eol(s):
    if s.endswith("\r\n"):
        return s[:-2]
    elif s.endswith("\r") or s.endswith("\n"):
        return s[:-1]
    else:
        return s

####################################################################################################

def print_freq(results, n):
    for (line, count) in results.top(n):
        line = strip_eol(line)
        print("%i %s" % (count, line))

####################################################################################################

def freq(paths, db_path, n, line_filter):
    """
    Reads the paths from the given list of paths and prints the most-frequently-occuring lines.
    The "paths" parameter must be an iterable that returns strings.  For each string returned that
    file is opened and its lines read.  If None is returned then standard input is read.  The "n"
    parameter must be an int.  If the value of "n" is greater than zero then the top n lines are
    printed; if less than zero then the bottom -n lines are printed; otherwise, all distinct lines
    are printed.  The "line_filter" parameter must be a function that will be specified each line
    as a string; if it returns None then the line will be discarded; otherwise, the returned string
    will be used as the line's value; may be None to perform no filtering.  Raises GeneralException
    on error.
    """
    results = FreqDb(db_path)

    results.open()
    try:
        for path in paths:
            freq_path(path, results, line_filter)
        results.commit()
        print_freq(results, n)
    finally:
        results.close()

####################################################################################################

def main():
    """
    The main method for this application.
    """
    settings = parse_args()
    paths = iter_paths(settings.files)
    db_path = settings.db_path
    n = settings.n
    line_filter = LineFilter(settings.trim, settings.include_empty_lines)
    freq(paths, db_path, n, line_filter)

####################################################################################################

if __name__ == "__main__":
    try:
        main()
    except ArgumentParseException as e:
        if e.exit_code != 0:
            print("ERROR: invalid command-line arguments: %s" % e, file=sys.stderr)
            print("Run with --help for help", file=sys.stderr)
            sys.exit(e.exit_code)
    except GeneralException as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)

    sys.exit(0)
