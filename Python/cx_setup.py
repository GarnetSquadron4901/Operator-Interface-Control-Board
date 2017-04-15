from cx_Freeze import setup, Executable
import sys
import os

os.environ['TCL_LIBRARY'] = r'C:\Python35\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Python35\tcl\tk8.6'

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [Executable(
    script='ControlBoardApp\\ControlBoardApp.py',
    base=base,
    icon='ControlBoardApp\\ControlBoard.ico',
    shortcutName="Control Board",
    shortcutDir="DesktopFolder",
)]


build_exe_options = {"packages": [
            'crccheck',
            'numpy',
            'pyfrc',
            'networktables',
            'serial',
            'wx',
            'os',
            'sys',
            "ControlBoardApp",
            "ControlBoardApp._version",
            "ControlBoardApp.cbhal",
            "ControlBoardApp.GUI"
            ], "excludes": None}

# This gets __version__
exec(open('ControlBoardApp\\_version.py').read())

setup(
    name='ControlBoardApp',
    version = str(__version__),
    description='Control board application for the FRC Driver Station Control Board',
    options = {"build_exe": build_exe_options},
    executables=executables

)