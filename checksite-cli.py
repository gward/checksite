#!/usr/local/bin/python

import importlib
import os
import sys

import checksite

# Poor man's version of click. This is all the functionality I need here,
# so adding click feels like overkill.
try:
    cmd = sys.argv.pop(1)
    mod = importlib.import_module('checksite.' + cmd)
except IndexError:
    sys.exit('error: not enough arguments\n\nusage: %s cmd' % (sys.argv[0],))
except ModuleNotFoundError:
    sys.exit('error: invalid command: %s' % (cmd,))
else:
    mod.main(os.environ)
