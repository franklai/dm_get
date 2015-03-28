from distutils.core import setup
import py2exe

import dm_get

setup(
    console = [
        {
            "script": "dm_get.py",
        }
    ],
    options = {
        "py2exe": {
            "optimize": 2,
            "compressed": 1,
            "bundle_files": 1,
            "includes": dm_get.get_module_list(),
            "packages": ['requests']
        }
    },
    zipfile = None,
    data_files = [('', ['input.txt',])]
)

