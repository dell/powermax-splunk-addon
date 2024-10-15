# encode = utf-8

"""
This module is used to filter and reload PATH.
This file is genrated by Splunk add-on builder
"""

import os
import sys
import re

if sys.version_info[0] < 3:
    py_version = "aob_py2"
else:
    py_version = "aob_py3"

ta_name = 'TA-DellEMC_VMAX'
py_lib_dir = 'py_lib_dir'
pyu4v_name = 'PyU4V'

pattern = re.compile(r"[\\/]etc[\\/]apps[\\/][^\\/]+[\\/]bin[\\/]?$")
new_paths = [path for path in sys.path if not pattern.search(path) or ta_name in path]
new_paths.insert(0, os.path.sep.join([os.path.dirname(__file__), py_lib_dir]))
new_paths.insert(0, os.path.sep.join([os.path.dirname(__file__), py_lib_dir, py_version]))
new_paths.insert(0, os.path.sep.join([os.path.dirname(__file__), py_lib_dir, py_version, pyu4v_name]))
sys.path = new_paths