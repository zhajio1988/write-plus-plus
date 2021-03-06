"""
setup.py - builds executable for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

from distutils.core import setup
from py2exe.build_exe import py2exe

import glob
import os
import shutil
import sys

_version = "0.9.9"
manifest = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
    <assemblyIdentity version="0.64.1.0" processorArchitecture="x86"
    name="Controls" type="win32"/>
    <description>%s</description>
    <dependency>
        <dependentAssembly>
            <assemblyIdentity type="win32"
            name="Microsoft.Windows.Common-Controls" version="6.0.0.0"
            processorArchitecture="X86" publicKeyToken="6595b64144ccf1df"
            language="*"/>
        </dependentAssembly>
    </dependency>
    <dependency>
        <dependentAssembly>
            <assemblyIdentity type="win32"
            name="Microsoft.VC90.CRT" version="9.0.21022.8"
            processorArchitecture="x86" publicKeyToken="1fc8b3b9a1e18e3b" />
        </dependentAssembly>
    </dependency>
</assembly>"""
cwd = os.path.dirname(__file__)
os.chdir(cwd)

class Target:
    def __init__(self):
        self.dest_base = "write++"
        self.name = "Write++"
        self.version = _version
        self.company_name = "Timothy Johnson"
        self.copyright = "Copyright \xa9 2011-2013 Timothy Johnson. All rights reserved."
        self.description = self.name
        self.icon_resources = [(1, "write++.ico")]
        self.bitmap_resources = []
        self.other_resources = [(24, 1, manifest % self.name)]
        self.script = "write++.py"

if os.path.isdir("dist"):
    shutil.rmtree("dist")
sys.path.append("C:\\WINDOWS\\WinSxS\\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.21022.8_x-ww_d08d0375")

setup(data_files=[("images", glob.glob("images\\*.*")),
                  ("locale\\en_US", glob.glob("locale\\en_US\\*.*")),
                  ("locale\\en_US\\help", glob.glob("locale\\en_US\\help\\*.*")),
                  ("locale\\en_US\\help\\images", glob.glob("locale\\en_US\\help\\images\\*.*")),
                  ("", ["license.txt", "styles.xml"])],
    options={"py2exe":{"optimize":2,
                       "compressed":1,
                       "bundle_files":3,
                       "includes":["lxml._elementpath"],
                       "packages":["syntax"],
                       "excludes":["_gtkagg", "_tkagg", "bsddb", "curses", "email", "pywin.debugger",
                        "pywin.debugger.dbgcon", "pywin.dialogs", "tcl",
                        "Tkconstants", "Tkinter", "_winxptheme"],
                       "dll_excludes":["libgdk-win32-2.0-0.dll", "libgobject-2.0-0.dll", "tcl85.dll",
                        "tk85.dll", "msvcr80.dll", "UxTheme.dll", "w9xpopen.exe"],
                       "xref":False,
                       "ascii":False,
                       "skip_archive":False,
                       "custom_boot_script":""}},
    zipfile=None,
    console=[],
    windows=[Target()],
    service=[],
    com_server=[],
    ctypes_com_server=[])

if os.path.isdir("build"):
    shutil.rmtree("build")
