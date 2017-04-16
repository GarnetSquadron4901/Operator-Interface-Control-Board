import logging
import wx
from wx.adv import TaskBarIcon as TBI
import os
import sys

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.ControlBoardApp import APP_NAME
else:
    # Test Mode
    from ControlBoardApp import APP_NAME


def get_icon_path(icon_filename):
    """
    Returns the full path the the provided icon_filename.
    :param icon_filename: str - icon filename
    :return: 
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), icon_filename))


# Taskbar status icons
NULL_ICON = get_icon_path('Status_Null.ico')
CTRLB_NO_NT_NO = get_icon_path('Status_NoCtrlB_NoNT.ico')
CTRLB_NO_NT_YES = get_icon_path('Status_NoCtrlB_YesNT.ico')
CTRLB_YES_NT_NO = get_icon_path('Status_YesCtrlB_NoNT.ico')
CTRLB_YES_NT_YES = get_icon_path('Status_YesCtrlB_YesNT.ico')
CTRLB_YES_NT_DIS = get_icon_path('Status_YesCtrlB_DisNT.ico')
CTRLB_NO_NT_DIS = get_icon_path('Status_NoCtrlB_DisNT.ico')


class TaskBarIcon(TBI):
    def __init__(self, parent):
        """
        TaskBarIcon - used to show the taskbar icon.
        
        :param parent: wx parent
        """

        self.parent = parent
        self.logger = logging.getLogger(__name__)

        self.icon = NULL_ICON
        self.status = 0

        super(TaskBarIcon, self).__init__()
        self.set_icon(self.icon)
        # self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnDoubleClick)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRightClick)

    def OnDoubleClick(self, _):
        """
        Responds to the user double clicking the taskbar icon & shows the data window.
        :param _: 
        :return: 
        """
        self.logger.debug('User double clicked taskbar icon')
        self.OnShowWindow()

    def OnShowDataButtonPressed(self, _):
        """
        Responds to the Show Data button being pressed.
        
        :param _: 
        :return: 
        """
        self.logger.debug('User has clicked Show Data')
        self.OnShowWindow()

    def OnShowWindow(self):
        """
        Shows the parent window.
        
        :return: 
        """
        self.parent.show_window()

    def OnQuitButtonPressed(self, _):
        """
        Responds to the Quit button being pressed
        :param _: event - not used
        :return: 
        """
        self.logger.debug('User has clicked Quit')
        self.parent.exit_app()

    def CreatePopupMenu(self):
        """ Creates the popup menu.
        
        :return:
        """
        self.logger.debug('Creating popup menu')
        menu = wx.Menu()
        self._create_menu_item(menu, 'Show Data', self.OnShowDataButtonPressed)
        menu.AppendSeparator()
        self._create_menu_item(menu, 'Quit', self.OnQuitButtonPressed)
        return menu

    @staticmethod
    def _create_menu_item(menu, label, func):
        """
        Creates a wxMenuItem, binds the control, and appends it to the menu.
        
        :param menu: wxMenu
        :param label: str - new button label
        :param func: function pointer
        :return: 
        """
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.Append(item)
        return item

    def update_icon(self, ctrlb_good, nt_good, test_mode):
        """
        Updates the icon based on the parameters passed in
        :param ctrlb_good: bool - indicates a good control board connection
        :param nt_good: bool - indicates a good NT server connection
        :param test_mode: bool - indcates if the program is in Test mode. 
        :return: 
        """
        if not test_mode:
            if ctrlb_good:
                if nt_good:
                    icon_path = CTRLB_YES_NT_YES
                else:
                    icon_path = CTRLB_YES_NT_NO
            else:
                if nt_good:
                    icon_path = CTRLB_NO_NT_YES
                else:
                    icon_path = CTRLB_NO_NT_NO
        else:
            if ctrlb_good:
                icon_path = CTRLB_YES_NT_DIS
            else:
                icon_path = CTRLB_NO_NT_DIS

        self.set_icon(icon_path)

    def set_icon(self, icon_path):
        """
        Updates the task bar icon to indicate the current status.
        
        :param icon_path: str - file path to the icon 
        :return: 
        """
        if self.status is not icon_path:
            self.logger.debug('Updating taskbar icon to: %s' % icon_path)
            icon = wx.Icon()
            icon.CopyFromBitmap(wx.Bitmap(icon_path, wx.BITMAP_TYPE_ANY))
            self.SetIcon(icon, APP_NAME)
            self.status = icon_path

    # ----------------------------------------------------------------------
    @staticmethod
    def OnTaskBarActivate(_):
        """
        Overrides stock method to not do anything.
        
        :param _: event - not used
        :return: 
        """
        pass

    # ----------------------------------------------------------------------
    def OnTaskBarClose(self, _):
        """
        Destroy the taskbar icon and frame from the taskbar icon itself
        
        :param _: event - not used
        """
        self.frame.Close()

    # ----------------------------------------------------------------------
    def OnTaskBarRightClick(self, _):
        """
        Create the right-click menu
        
        :param _: event - not used
        """
        self.logger.debug('User right-clicked on the taskbar icon')
        menu = self.CreatePopupMenu()
        self.PopupMenu(menu)
        menu.Destroy()
