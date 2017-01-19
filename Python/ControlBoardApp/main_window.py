import wx, wx.html
import wx.lib.agw.hypertreelist as HTL
import ctypes
import os
import logging
import cbhal

from GUI.SetNtAddressDialog import SetAddressBox
from GUI.AboutBox import AboutBox
from GUI.TaskBarIcon import TaskBarIcon
from GUI.SetControlBoardType import SetControlBoardBox

logger = logging.getLogger(__name__)

# Main application icon
MAIN_ICON = os.path.abspath(os.path.join(os.path.split(__file__)[0], 'ControlBoard.ico'))

class MainWindow(wx.Frame):

    DEFAULT_STATUS = '-                           '

    def __init__(self, hal, nt, config):
        '''

        :param hal: cbhal.ControlBoardBase
        :param nt: NetworkTableAbstractionLayer
        :param config: config.ConfigFile
        '''
        wx.Frame.__init__(self, None, title='FRC Control Board')

        self.hal = hal
        self.nt = nt
        self.config = config

        self.log_window = wx.LogWindow(self, 'Control Board Log', False)

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
        self.menu_settings_setcb = self.menu_settings.Append(wx.ID_ANY, 'Set Control Board Type', 'Sets the type of control board you are using')
        self.Bind(wx.EVT_MENU, self.OnTestModeChanged, self.menu_settings_testmode)
        self.Bind(wx.EVT_MENU, self.OnSetNtAddress, self.menu_settings_setaddy)
        self.Bind(wx.EVT_MENU, self.OnCbSet, self.menu_settings_setcb)


        # Help menu
        self.menu_help = wx.Menu()
        self.menu_help_log = self.menu_help.Append(wx.ID_ANY, 'Show Log', 'Shows the current run log')
        self.menu_help_help = self.menu_help.Append(wx.ID_ANY, 'Help', 'Shows the documentation for the control board and application')
        self.menu_help_about = self.menu_help.Append(wx.ID_ANY, 'About', 'About this application')
        self.Bind(wx.EVT_MENU, self.OnShowLog, self.menu_help_log)
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

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'Control Board Type')
        self.hal_type = wx.StaticText(self, label=cbhal.types[self.config.get_cb_type()]['name'])
        self.tree.SetItemWindow(label, self.hal_type, 1)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'Control Board Status')
        self.hal_status = wx.StaticText(self, label=self.DEFAULT_STATUS)
        self.tree.SetItemWindow(label, self.hal_status, 1)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'NT Server Address')
        self.nt_address = wx.StaticText(self, label=self.DEFAULT_STATUS)
        self.tree.SetItemWindow(label, self.nt_address, 1)

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




        self.update_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnUpdateTimerEvent, self.update_timer)
        self.update_timer.Start(500)

        self.OnTestModeChanged()

        self.update_indicators()

        self.SetAutoLayout(True)
        self.Layout()

    def OnShowLog(self, _=None):
        self.log_window.Show()

    def OnUpdateTimerEvent(self, _=None):
        self.update_indicators()

    def OnTestModeChanged(self, _=None):
        wx.LogVerbose('Test mode is %s' % ('on' if self.isTestModeEnabled() else 'off'))
        if self.isTestModeEnabled():
            wx.LogWarning('Test mode disables Control Board and Robot communication.')

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
        cur_remote_address = self.nt.getNtServerAddress()
        ntdlg = SetAddressBox(self, cur_remote_address)
        ntdlg.ShowModal()
        if ntdlg.okPressed():
            new_remote_address = ntdlg.getAddress()
            if new_remote_address != self.config.get_nt_server_address():
                self.config.set_nt_server_address(new_remote_address)
                self.nt.setNtServerAddress(new_remote_address)
        ntdlg.Destroy()

    def OnCbSet(self, _=None):
        cbdlg = SetControlBoardBox(self, self.config.get_cb_type())
        cbdlg.ShowModal()
        if cbdlg.okPressed():
            if cbdlg.get_cb_type_sel() != self.config.get_cb_type():
                self.config.set_cb_type(cbdlg.get_cb_type_sel())
                self.hal_type.SetLabelText(cbdlg.get_cb_type_name())
                #TODO: Reload HAL somehow. This will currently only work after the user restarts the entire program
                cbdlg.Destroy()

    def OnAbout(self, _=None):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self, _=None):
        self.LogVerbose('Help button pressed')

    def hide_window(self, _=None):
        self.Hide()

    def show_window(self, _=None):
        self.Show()
        self.update_indicators()

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

    def event_responder(self):
        if self.isTestModeEnabled():
            self.nt.putNtData()
            wx.CallAfter(self.updateHalWithTestValues)
        else:
            self.nt.update()
        wx.CallAfter(self.update_indicators)

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

    def update_indicators(self):

        hal_status = self.hal.get_status()

        self.tb_icon.update_icon(ctrlb_good=hal_status['IsRunning'], nt_good=self.nt.isConnected())

        if self.IsShown():

            self.update_tree_status(self.hal_status, self.get_hal_status(is_running=hal_status['IsRunning'],
                                                                     state=hal_status['State'],
                                                                     update_rate=hal_status['UpdateRate']))
            self.update_tree_status(self.nt_address, self.nt.getNtServerAddress())
            self.update_tree_status(self.ntal_status, 'Connected' if self.nt.isConnected() else 'Disconnected')


            if hal_status['IsRunning']:

                for channel in range(self.hal.ANALOG_INPUTS):
                    self.update_tree_status(self.ANA_Status[channel], hal_status['ANAs'][channel])

                for channel in range(self.hal.SWITCH_INPUTS):
                    self.update_tree_status(self.SW_Status[channel], 'Closed' if hal_status['SWs'][channel] else 'Open')

                for channel in range(self.hal.LED_OUTPUTS):
                    self.update_tree_status(self.LED_Status[channel], 'On' if hal_status['LEDs'][channel] else 'Off')

                for channel in range(self.hal.PWM_OUTPUTS):
                    self.update_tree_status(self.PWM_Status[channel], hal_status['PWMs'][channel])


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
