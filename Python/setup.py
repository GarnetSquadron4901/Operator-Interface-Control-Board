import os
import sys
from setuptools import setup, find_packages
from os.path import expanduser, join


version_file = os.path.join(
            os.path.dirname(__file__),
            "ControlBoardApp",
            "_version.py")
exec(open(version_file).read())

setup(
    name='ControlBoardApp',
    version=str(__version__),
    description='Control board application for the FRC Driver Station Control Board',
    author='Ryan Nazaretian',
    author_email='ryannazaretian@gmail.com',
    include_package_data=True,
    packages=['ControlBoardApp', 'ControlBoardApp.hal'],
    package_data={'': ['*.xml', '*.ico', '*.png']},
    entry_points={
        'gui_scripts': ['ControlBoardApp = ControlBoardApp:main']
    },
    dependency_links = [


    ]
)

try:
    if sys.platform == 'win32' and sys.argv[1] in ['install', 'uninstall', 'develop']:
        from win32com.shell import shell, shellcon
        from win32com.client import Dispatch
        import site

        # Get paths to the desktop and start menu
        desktop_path = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
        startmenu_path = shell.SHGetFolderPath(0, shellcon.CSIDL_STARTMENU, None, 0)  

        print
        'Desktop:', desktop_path
        print
        'Start Menu:', startmenu_path

        if sys.argv[1] == 'uninstall':
            print('Removing shortcuts.')
            for path in [desktop_path, startmenu_path]:
                if os.path.isfile(path):
                    os.remove(path)

        if sys.argv[1] == 'install' or sys.argv[1] == 'develop':
            print('#' * 100)
            print('#' * 100)
            print('Creating shortcuts.')

            shortcut_filename = "Control Board.lnk"
            working_dir = expanduser('~')
            script_path = join(sys.prefix, "Scripts", "ControlBoardApp.exe")
            site_packages = site.getsitepackages()

            for site_package in site_packages:
                icon = version_file = os.path.join(
                    site_package,
                    "ControlBoardApp",
                    "ControlBoard.ico")
                print('Looking for icon in:', icon)
                if os.path.isfile(icon):
                    print('Found icon in path:', icon)
                    # Create shortcuts.
                    for path in [desktop_path, startmenu_path]:
                        shortcut_path = join(path, shortcut_filename)
                        print('Creating shortcut at "%s"' % shortcut_path)
                        shell = Dispatch('WScript.Shell')
                        shortcut = shell.CreateShortCut(shortcut_path)
                        shortcut.Targetpath = script_path
                        shortcut.WorkingDirectory = working_dir
                        shortcut.IconLocation = icon
                        shortcut.save()
                    break
except Exception as e:
    print('Error installing/uninstalling shortcuts:', str(e))
