from distutils.version import LooseVersion

# MAJOR ----------
# FRC Year
FRC_YEAR = 2018

# MAJOR ------------
# Big feature release
# 0 - beta
# 1+ - release
FEATURE = 2

# MINOR ------
BUILD = 0

__version__ = LooseVersion("{frc_year}.{feature}.{build}".format(
    frc_year=FRC_YEAR,
    feature=FEATURE,
    build=BUILD))
