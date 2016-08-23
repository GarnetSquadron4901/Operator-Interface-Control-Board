import wx
import wx.lib.agw.hypertreelist as HTL
from wx.adv import TaskBarIcon as TBI
import time
import ctypes
import os

from ControlBoardApp import hal
from ControlBoardApp import ntal
from threading import Event, Thread

ADDRESS = 'localhost'

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
    def __init__(self):

        self.icon = CTRLB_NO_NT_NO
        self.status = 0

        super(TaskBarIcon, self).__init__()
        self.set_icon(self.icon)
        # self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self._create_menu_item(menu, 'Show Data', self.on_hello)
        menu.AppendSeparator()
        self._create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    @staticmethod
    def _create_menu_item(menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item

    def update_icon(self, ctrlb_good, nt_good):

        status_sel = int(bool(ctrlb_good) << 1 | bool(nt_good))
        if self.status is not status_sel:
            self.set_icon(STATUS_ICON[status_sel])
            self.status = status_sel

    def set_icon(self, path):
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap(path, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print ('Tray icon was left-clicked.')

    def on_hello(self, event):
        print ('Hello, world!')

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)

class MainWindow(wx.Frame):

    DEFAULT_STATUS = '-                           '

    def __init__(self, hal, nt):
        wx.Frame.__init__(self, None, title='Garnet Controls')

        self.hal = hal
        self.nt = nt

        # Set Icon
        # Setup the icon
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(wx.Bitmap(MAIN_ICON, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        # Windows isn't smart enough to pull the right icon (it looks at the EXE), point it to look at this script's
        # icon
        # from http://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-
        # 7/1552105#1552105
        myappid = u'ControlBoard.1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Set Taskbar Icon
        self.tb_icon = TaskBarIcon()

        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

        self.tree = HTL.HyperTreeList(parent=self,
                                      id=wx.ID_ANY,
                                      agwStyle=wx.TR_DEFAULT_STYLE |
                                               wx.TR_EDIT_LABELS |
                                               wx.TR_HIDE_ROOT,
                                      )
        self.tree.AddColumn('Name')
        self.tree.AddColumn('Status')
        self.tree.SetColumnWidth(0, 150)
        self.tree.SetColumnWidth(1, 150)
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
            # h_sizer = wx.BoxSizer()
            label = self.tree.AppendItem(self.switch_status, 'SW ' + str(array_index))
            item = wx.StaticText(self, label=self.DEFAULT_STATUS)
            self.SW_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.v_sizer.Add(self.tree, 1, wx.EXPAND, 0)
        self.SetSizer(self.v_sizer)
        self.SetAutoLayout(True)
        self.Layout()

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

def main():
    cb_hal = hal.HardwareAbstractionLayer(debug=True)
    nt = ntal.NetworkTableAbstractionLayer(address=ADDRESS, hal=cb_hal)
    app = wx.App()
    frame = MainWindow(hal=cb_hal, nt=nt)
    cb_hal.set_event_handler(frame.event_responder)
    cb_hal.start()
    frame.Show()
    app.MainLoop()
    cb_hal.stop()

if __name__ == '__main__':
    main()
