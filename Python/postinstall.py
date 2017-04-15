import os
import sys
import ControlBoardApp
import shutil


# Get paths to the desktop and start menu
DESKTOP_FOLDER = get_special_folder_path('CSIDL_DESKTOPDIRECTORY')
STARTMNEU_FOLDER = get_special_folder_path('CSIDL_COMMON_STARTMENU')
NAME = "Control Board.lnk"

print('Desktop:    %s' % DESKTOP_FOLDER)
print('Start Menu: %s' % STARTMNEU_FOLDER)

if sys.argv[1] == '-install':

    # Create shortcuts.
    for final_path in [DESKTOP_FOLDER, STARTMNEU_FOLDER]:

        create_shortcut(
            os.path.join(sys.prefix, 'pythonw.exe'), # program
            'Control Board Application', # description
            NAME, # filename
            ControlBoardApp.__file__, # parameters
            '', # workdir
            os.path.join(os.path.dirname(ControlBoardApp.__file__), 'ControlBoard.ico') # iconpath
        )

        # move shortcut from current directory to DESKTOP_FOLDER
        shutil.move(os.path.join(os.getcwd(), NAME),
                    os.path.join(final_path, NAME))

        # tell windows installer that we created another
        # file which should be deleted on uninstallation
        file_created(os.path.join(final_path, NAME))

if sys.argv[1] == '-remove':
    for final_path in [DESKTOP_FOLDER, STARTMNEU_FOLDER]:
        if os.path.isfile(final_path):
            os.remove(final_path)

