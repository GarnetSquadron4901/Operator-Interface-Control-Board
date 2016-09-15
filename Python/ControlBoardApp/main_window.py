import wx
import wx.lib.agw.hypertreelist as HTL
from wx.adv import TaskBarIcon as TBI
import ctypes
import os

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
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.parent.show_window())

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self._create_menu_item(menu, 'Show Data', self.parent.show_window())
        menu.AppendSeparator()
        self._create_menu_item(menu, 'Exit', self.parent.exit_app())
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
        self.menu_file_quit = self.menu_file.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.exit_app, self.menu_file_quit)

        # Settings menu
        self.menu_settings = wx.Menu()
        self.menu_settings_testmode = self.menu_settings.AppendCheckItem(wx.ID_ANY, 'Test Mode', 'Enable/Disable Test Mode')
        self.menu_settings_setaddy = self.menu_settings.Append(wx.ID_ANY, 'Set NT Address', 'Set the robot\'s address to access the Network Table server')
        self.Bind(wx.EVT_MENU, self.OnTestModeChanged, self.menu_settings_testmode)
        self.Bind(wx.EVT_MENU, self.OnSetRobotAddress, self.menu_settings_setaddy)


        # Help menu
        self.menu_help = wx.Menu()
        self.menu_help_help = self.menu_help.Append(wx.ID_ANY, 'Help', 'Shows the documentation for the control board and application')
        self.menu_help_about = self.menu_help.Append(wx.ID_ANY, 'About', 'About this application')


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
        for array_index in range(self.hal.LED_OUTPUTS):
            label = self.tree.AppendItem(self.led_status, 'LED ' + str(array_index))
            item = wx.StaticText(self, label=self.DEFAULT_STATUS)
            self.LED_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.PWM_Status = []
        for array_index in range(self.hal.PWM_OUTPUTS):
            label = self.tree.AppendItem(self.pwm_status, 'PWM ' + str(array_index))
            item = wx.StaticText(self, label=self.DEFAULT_STATUS)
            self.PWM_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

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

        self.Bind(event=wx.EVT_CLOSE, handler=self.hide_window())

        self.tree.CalculateAndSetHeaderHeight()
        self.tree.DoHeaderLayout()
        self.tree.SetColumnWidth(0, self.tree.DoGetBestSize().GetWidth())

        self.v_sizer.Add(self.tree, 1, wx.EXPAND, 0)

        self.tree.InvalidateBestSize()
        self.v_sizer.SetMinSize(self.tree.GetBestSize())

        self.Bind(wx.EVT_CLOSE, self.exit_app)


        self.SetSizer(self.v_sizer)
        self.SetMenuBar(self.menu)

        self.SetAutoLayout(True)
        self.Layout()

    def OnTestModeChanged(self, event):
        print('Test mode changed!')

    def OnSetRobotAddress(self, event):
        pass

    def hide_window(self):
        self.Hide()

    def show_window(self):
        self.Show()

    def exit_app(self, _):
        self.hal.set_event_handler(None)
        self.hal.stop()
        self.tb_icon.Destroy()
        self.Hide()
        self.Destroy()

    def event_responder(self, event):
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

        if self.IsShown():

            self.update_tree_status(self.hal_status, self.get_hal_status(is_running=data['IsRunning'],
                                                                     state=data['State'],
                                                                     update_rate=data['UpdateRate']))
            self.update_tree_status(self.ntal_status, 'Connected' if self.nt.isConnected() else 'Disconnected')

            self.tb_icon.update_icon(ctrlb_good=data['IsRunning'], nt_good=self.nt.isConnected())

            if data['IsRunning']:

                for channel in range(self.hal.LED_OUTPUTS):
                    self.update_tree_status(self.LED_Status[channel], 'On' if data['LEDs'][channel] else 'Off')

                for channel in range(self.hal.PWM_OUTPUTS):
                    self.update_tree_status(self.PWM_Status[channel], data['PWMs'][channel])

                for channel in range(self.hal.ANALOG_INPUTS):
                    self.update_tree_status(self.ANA_Status[channel], data['ANAs'][channel])

                for channel in range(self.hal.SWITCH_INPUTS):
                    self.update_tree_status(self.SW_Status[channel], 'Closed' if data['SWs'][channel] else 'Open')
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
