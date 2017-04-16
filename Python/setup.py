import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version_file = os.path.join(
            os.path.dirname(__file__),
            "ControlBoardApp",
            "version.py")

# This gets __version__
exec(open(version_file).read())

REQUIREMENTS = [
        'crccheck',
        'numpy',
        'pyfrc',
        'pynetworktables',
        'pyserial',
        'wxPython_Phoenix',
    ]

setup(
    name='ControlBoardApp',
    version=str(__version__),
    description='Control board application for the FRC Driver Station Control Board',
    author='Ryan Nazaretian',
    author_email='ryannazaretian@gmail.com',
    url='https://github.com/GarnetSquadron4901/Operator-Interface-Control-Board',
    include_package_data=True,
    packages=['ControlBoardApp', 'ControlBoardApp.cbhal', 'ControlBoardApp.GUI'],
    scripts=['postinstall.py'],
    package_data={'': ['*.xml', '*.ico', '*.png']},
    entry_points={
        'gui_scripts': ['ControlBoardApp = ControlBoardApp:main']
    },
    requires=REQUIREMENTS,
    install_requires=REQUIREMENTS,
    dependency_links=[
        'https://wxpython.org/Phoenix/snapshot-builds#egg=wxPython_Phoenix-3.0.3.dev2648+23be602-cp35-cp35'
    ]
)




