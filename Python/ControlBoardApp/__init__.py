import sys

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.ControlBoardApp import *
else:
    # Test Mode
    from ControlBoardApp import *

# If main, call main
if __name__ == '__main__':
    main()
