################################################################################
#
# freq2.py
# By: Denver Coneybeare <denver.coneybeare@gmail.com>
# August 24, 2011
#
# Copyright 2011 Denver Coneybeare
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

import sys

################################################################################

class ArgumentParseError(Exception):
    def __init__(self, exit_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exit_code = exit_code

################################################################################

class FreqApplicationError(Exception):
    def __init__(self, exit_code, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exit_code = exit_code

################################################################################

class FreqApplication:

    def __init__(self, program_name, args):
        self.program_name = program_name
        self.args = tuple(args)

    def main(self):
        try:
            self.run()
        except FreqApplicationError as e:
            print("ERROR: {}".format(e), file=sys.stderr)
            exit_code = e.exit_code
            if exit_code == 2:
                print("Run with --help for help", file=sys.stderr)
        except KeyboardInterrupt:
            print("ERROR: application terminated by keyboard interrupt",
                file=sys.stderr)
            exit_code = 1
        else:
            exit_code = 0

        sys.exit(exit_code)

    def run(self):
        pass

################################################################################

if __name__ == "__main__":
    app = FreqApplication(sys.argv[0], sys.argv[1:])
    app.main()
