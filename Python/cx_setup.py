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
    shortcutName='Control Board',
    shortcutDir='DesktopFolder',
)]


build_exe_options = {'packages': [
				'crccheck',
				'numpy',
				'pyfrc',
				'networktables',
				'serial',
				'wx',
				'os',
				'sys',
				'ControlBoardApp',
				'ControlBoardApp.version',
				'ControlBoardApp.cbhal',
				'ControlBoardApp.GUI'
            ], 
			'excludes': None,
			'include_files': [
				'help.pdf'
			]}

# This gets __version__
exec(open('ControlBoardApp\\version.py').read())

setup(
    name='Operator Interface Control Board',
	author='Ryan Nazaretian',
	author_email='ryannazaretian@gmail.com',
	url='https://github.com/GarnetSquadron4901/Operator-Interface-Control-Board',
    version = str(__version__),
    description='Application for the Operator Interface Control Board',
    options = {'build_exe': build_exe_options},
    executables=executables

)