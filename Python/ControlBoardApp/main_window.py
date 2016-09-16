import wx, wx.html
import wx.lib.agw.hypertreelist as HTL
from wx.adv import TaskBarIcon as TBI
import ctypes
import os
import sys
import ControlBoardApp._version as ntcbaver
import networktables.version as ntver

# Main application icon
MAIN_ICON = os.path.abspath(os.path.join(os.path.split(__file__)[0], 'ControlBoard.ico'))

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

        self.icon = CTRLB_NO_NT_NO
        self.status = 0

        super(TaskBarIcon, self).__init__()
        self.set_icon(self.icon)
        # self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.parent.show_window)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRightClick)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self._create_menu_item(menu, 'Show Data', self.parent.show_window)
        menu.AppendSeparator()
        self._create_menu_item(menu, 'Quit', self.parent.exit_app)
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
        menu = self.CreatePopupMenu()
        self.PopupMenu(menu)
        menu.Destroy()

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnLinkClicked)

    def OnLinkClicked(self, event):
        os.startfile(event.GetLinkInfo().GetHref())

aboutText = """<p>FRC Control Board Application: %(cbaver)s</p>
<p>pynetworktables: %(ntver)s</p>
<p>wxPython: %(wxpy)s</p>
<p>Python: %(python)s</p>
<p>See <a href="http://github.com/GarnetSquardon4901/Operator-Interface-Control-Board">FRC Control Board Documentation</a></p>
"""
class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About FRC Control Board",
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400,200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        vers["cbaver"] = str(ntcbaver.__version__)
        vers["ntver"] = str(ntver.__version__)
        hwin.SetPage(aboutText % vers)
        btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class MainWindow(wx.Frame):

    DEFAULT_STATUS = '-                           '

    def __init__(self, hal, nt):
        wx.Frame.__init__(self, None, title='FRC Control Board')

        self.hal = hal
        self.nt = nt

        # Set Icon
        # Setup the icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(MAIN_ICON, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        # Windows isn't smart enough to pull the right icon (it looks at the EXE), point it to look at this script's
        # icon
        # from http://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-
        # 7/1552105#1552105
        myappid = u'ControlBoardApp.1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Set Taskbar Icon
        self.tb_icon = TaskBarIcon(self)

        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

        ########################################
        # Menu bar configuration

        # File menu
        self.menu_file = wx.Menu()
        self.menu_file_hide = self.menu_file.Append(wx.ID_ANY, 'Hide', 'Hide this window. Application continues running in the background.')
        self.menu_file_quit = self.menu_file.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.hide_window, self.menu_file_hide)
        self.Bind(wx.EVT_MENU, self.exit_app, self.menu_file_quit)

        # Settings menu
        self.menu_settings = wx.Menu()
        self.menu_settings_testmode = self.menu_settings.AppendCheckItem(wx.ID_ANY, 'Test Mode', 'Enable/Disable Test Mode')
        self.menu_settings_setaddy = self.menu_settings.Append(wx.ID_ANY, 'Set NT Address', 'Set the robot\'s address to access the Network Table server')
        self.Bind(wx.EVT_MENU, self.OnTestModeChanged, self.menu_settings_testmode)
        self.Bind(wx.EVT_MENU, self.OnSetNtAddress, self.menu_settings_setaddy)


        # Help menu
        self.menu_help = wx.Menu()
        self.menu_help_help = self.menu_help.Append(wx.ID_ANY, 'Help', 'Shows the documentation for the control board and application')
        self.menu_help_about = self.menu_help.Append(wx.ID_ANY, 'About', 'About this application')
        self.Bind(wx.EVT_MENU, self.OnHelp, self.menu_help_help)
        self.Bind(wx.EVT_MENU, self.OnAbout, self.menu_help_about)


        # Create menu bar
        self.menu = wx.MenuBar()
        self.menu.Append(self.menu_file, 'File')
        self.menu.Append(self.menu_settings, 'Settings')
        self.menu.Append(self.menu_help, 'Help')

        # End menu bar configuration
        ########################################

        self.tree = HTL.HyperTreeList(parent=self,
                                      id=wx.ID_ANY,
                                      agwStyle=wx.TR_DEFAULT_STYLE |
                                               wx.TR_EDIT_LABELS |
                                               wx.TR_HIDE_ROOT,
                                      )
        self.tree.AddColumn('Name')
        self.tree.AddColumn('Status')
        self.tree.AddColumn('Test Mode')
        self.tree.AddRoot('Root')
        self.tree.SetMainColumn(0)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'Control Board Status')
        self.hal_status = wx.StaticText(self, label=self.DEFAULT_STATUS)
        self.tree.SetItemWindow(label, self.hal_status, 1)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'Network Table')
        self.ntal_status = wx.StaticText(self, label=self.DEFAULT_STATUS)
        self.tree.SetItemWindow(label, self.ntal_status, 1)

        self.analog_status = self.tree.AppendItem(self.tree.GetRootItem(), 'Analog Inputs')
        self.led_status = self.tree.AppendItem(self.tree.GetRootItem(), 'LED Outputs')
        self.pwm_status = self.tree.AppendItem(self.tree.GetRootItem(), 'PWM Outputs')
        self.switch_status = self.tree.AppendItem(self.tree.GetRootItem(), 'Switch Inputs')

        self.LED_Status = []
        self.LED_Test = []
        for array_index in range(self.hal.LED_OUTPUTS):
            label = self.tree.AppendItem(self.led_status, 'LED ' + str(array_index))
            item = wx.StaticText(self, label=self.DEFAULT_STATUS)
            test = wx.CheckBox(self)
            self.LED_Status.append(item)
            self.LED_Test.append(test)
            self.tree.SetItemWindow(label, item, 1)
            self.tree.SetItemWindow(label, test, 2)

        self.PWM_Status = []
        self.PWM_Test = []
        for array_index in range(self.hal.PWM_OUTPUTS):
            label = self.tree.AppendItem(self.pwm_status, 'PWM ' + str(array_index))
            item = wx.StaticText(self, label=self.DEFAULT_STATUS)
            test = wx.Slider(self)
            test.SetMin(0)
            test.SetMax(255)
            self.PWM_Test.append(test)
            self.PWM_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)
            self.tree.SetItemWindow(label, test, 2)

        self.ANA_Status = []
        for array_index in range(self.hal.ANALOG_INPUTS):
            label = self.tree.AppendItem(self.analog_status, 'ANA ' + str(array_index))
            item = wx.StaticText(self, label=self.DEFAULT_STATUS)
            self.ANA_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.SW_Status = []
        for array_index in range(self.hal.SWITCH_INPUTS):
            label = self.tree.AppendItem(self.switch_status, 'SW ' + str(array_index))
            item = wx.StaticText(self, label=self.DEFAULT_STATUS)
            self.SW_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.Bind(wx.EVT_CLOSE, self.hide_window)

        self.tree.CalculateAndSetHeaderHeight()
        self.tree.DoHeaderLayout()
        self.tree.SetColumnWidth(0, self.tree.DoGetBestSize().GetWidth())

        self.v_sizer.Add(self.tree, 1, wx.EXPAND, 0)

        self.tree.InvalidateBestSize()
        self.v_sizer.SetMinSize(self.tree.GetBestSize())

        self.Bind(wx.EVT_CLOSE, self.hide_window)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.update_test_elements)

        self.SetMenuBar(self.menu)

        self.SetSizer(self.v_sizer)

        self.SetAutoLayout(True)
        self.Layout()

        self.OnTestModeChanged()


    def OnTestModeChanged(self, _=None):
        print ('Test mode changed to', ('On' if self.isTestModeEnabled() else 'Off'))

        self.update_test_elements()
        self.tree.GetColumn(2).SetShown(self.isTestModeEnabled())
        self.tree.Refresh(True)
        self.tree.Update()
        self.Refresh(True)

    def update_test_elements(self, _=None):
        test_mode_enabled = self.isTestModeEnabled()

        if self.led_status.IsExpanded():
            for led in self.LED_Test:
                led.Show(test_mode_enabled)
            led.GetParent().Refresh()

        if self.pwm_status.IsExpanded():
            for pwm in self.PWM_Test:
                pwm.Show(test_mode_enabled)
            pwm.GetParent().Refresh()




    def OnSetNtAddress(self, _=None):
        print('Set NT address pressed')

    def OnAbout(self, _=None):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self, _=None):
        print('Help button pressed')

    def hide_window(self, _=None):
        self.Hide()

    def show_window(self, _=None):
        self.Show()

    def exit_app(self, _=None):
        self.hal.set_event_handler(None)
        self.hal.stop()
        self.tb_icon.Destroy()
        self.Hide()
        self.Destroy()

    def isTestModeEnabled(self):
        return self.menu_settings_testmode.IsChecked()

    def updateHalWithTestValues(self, _=None):
        self.hal.putLedValues([led.IsChecked() for led in self.LED_Test])
        self.hal.putPwmValues([pwm.GetValue() for pwm in self.PWM_Test])

    def event_responder(self, event):
        if self.isTestModeEnabled():
            self.nt.putNtData()
            wx.CallAfter(self.updateHalWithTestValues, event)
        else:
            self.nt.update()
        wx.CallAfter(self.update_indicators, event)

    def get_hal_status(self, is_running, state, update_rate):

        if is_running:
            if update_rate is not None:
                return 'Running, Updating @ ' + str(int(update_rate)) + ' Hz'
            else:
                return 'Running, Calculating update rate...'
        else:
            return state






    def update_tree_status(self, gui_element, status):
        if gui_element.GetLabelText() != str(status):
            gui_element.SetLabelText(str(status))

    def update_indicators(self, data):

        self.tb_icon.update_icon(ctrlb_good=data['IsRunning'], nt_good=self.nt.isConnected())

        if self.IsShown():

            self.update_tree_status(self.hal_status, self.get_hal_status(is_running=data['IsRunning'],
                                                                     state=data['State'],
                                                                     update_rate=data['UpdateRate']))
            self.update_tree_status(self.ntal_status, 'Connected' if self.nt.isConnected() else 'Disconnected')


            if data['IsRunning']:

                for channel in range(self.hal.ANALOG_INPUTS):
                    self.update_tree_status(self.ANA_Status[channel], data['ANAs'][channel])

                for channel in range(self.hal.SWITCH_INPUTS):
                    self.update_tree_status(self.SW_Status[channel], 'Closed' if data['SWs'][channel] else 'Open')

                for channel in range(self.hal.LED_OUTPUTS):
                    self.update_tree_status(self.LED_Status[channel], 'On' if data['LEDs'][channel] else 'Off')

                for channel in range(self.hal.PWM_OUTPUTS):
                    self.update_tree_status(self.PWM_Status[channel], data['PWMs'][channel])


            else:

                for channel in range(self.hal.LED_OUTPUTS):
                    self.update_tree_status(self.LED_Status[channel], '-')

                for channel in range(self.hal.PWM_OUTPUTS):
                    self.update_tree_status(self.PWM_Status[channel], '-')

                for channel in range(self.hal.ANALOG_INPUTS):
                    self.update_tree_status(self.ANA_Status[channel], '-')

                for channel in range(self.hal.SWITCH_INPUTS):
                    self.update_tree_status(self.SW_Status[channel], '-')

                self.Update()
