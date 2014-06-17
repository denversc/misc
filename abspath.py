#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

for path in sys.argv[1:]:
    abs_path = os.path.normpath(os.path.abspath(path))
    print(abs_path)

