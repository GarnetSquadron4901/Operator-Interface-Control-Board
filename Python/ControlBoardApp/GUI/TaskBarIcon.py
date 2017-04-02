import logging

import wx
from wx.adv import TaskBarIcon as TBI
import os

# Taskbar status icons
CTRLB_NO_NT_NO = os.path.abspath(os.path.join(os.path.split(__file__)[0], 'Status_NoCtrlB_NoNT.ico'))
CTRLB_NO_NT_YES = os.path.abspath(os.path.join(os.path.split(__file__)[0], 'Status_NoCtrlB_YesNT.ico'))
CTRLB_YES_NT_NO = os.path.abspath(os.path.join(os.path.split(__file__)[0], 'Status_YesCtrlB_NoNT.ico'))
CTRLB_YES_NT_YES = os.path.abspath(os.path.join(os.path.split(__file__)[0], 'Status_YesCtrlB_YesNT.ico'))
STATUS_ICON = [CTRLB_NO_NT_NO, CTRLB_NO_NT_YES, CTRLB_YES_NT_NO, CTRLB_YES_NT_YES]
TRAY_TOOLTIP = 'FRC Control Board'

class TaskBarIcon(TBI):
    def __init__(self, parent):

        self.parent = parent
        self.logger = logging.getLogger(__name__)

        self.icon = CTRLB_NO_NT_NO
        self.status = 0

        super(TaskBarIcon, self).__init__()
        self.set_icon(self.icon)
        # self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnDoubleClick)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRightClick)

    def OnDoubleClick(self, _):
        self.logger.debug('User double clicked taskbar icon')
        self.OnShowWindow()

    def OnShowDataButtonPressed(self, _):
        self.logger.debug('User has clicked Show Data')
        self.OnShowWindow()

    def OnShowWindow(self):
        self.parent.show_window()

    def OnQuitButtonPressed(self, _):
        self.logger.debug('User has clicked Quit')
        self.parent.exit_app()

    def CreatePopupMenu(self):
        self.logger.debug('Creating popup menu')
        menu = wx.Menu()
        self._create_menu_item(menu, 'Show Data', self.OnShowDataButtonPressed)
        menu.AppendSeparator()
        self._create_menu_item(menu, 'Quit', self.OnQuitButtonPressed)
        return menu

    @staticmethod
    def _create_menu_item(menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.Append(item)
        return item

    def update_icon(self, ctrlb_good, nt_good):
        status_sel = int(bool(ctrlb_good) << 1 | bool(nt_good))
        if self.status is not status_sel:
            self.logger.debug('Updating taskbar icon to: %s' % STATUS_ICON[status_sel])
            self.set_icon(STATUS_ICON[status_sel])
            self.status = status_sel

    def set_icon(self, path):
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(path, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon, TRAY_TOOLTIP)

    # ----------------------------------------------------------------------
    def OnTaskBarActivate(self, evt):
        """"""
        pass

    # ----------------------------------------------------------------------
    def OnTaskBarClose(self, evt):
        """
        Destroy the taskbar icon and frame from the taskbar icon itself
        """
        self.frame.Close()

    # ----------------------------------------------------------------------
    def OnTaskBarRightClick(self, evt):
        """
        Create the right-click menu
        """
        self.logger.debug('User right-clicked on the taskbar icon')
        menu = self.CreatePopupMenu()
        self.PopupMenu(menu)
        menu.Destroy()



