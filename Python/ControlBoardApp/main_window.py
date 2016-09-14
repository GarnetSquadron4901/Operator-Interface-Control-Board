import wx
import wx.lib.agw.hypertreelist as HTL
from wx.adv import TaskBarIcon as TBI
import ctypes
import os

from ControlBoardApp import hal
from ControlBoardApp import ntal

ADDRESS = '129.252.23.137'

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
        myappid = u'ControlBoard.1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Set Taskbar Icon
        self.tb_icon = TaskBarIcon(self)

        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

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


        self.SetSizer(self.v_sizer)
        self.SetAutoLayout(True)
        self.Layout()

    def hide_window(self):
        self.Hide()

    def show_window(self):
        self.Show()

    def exit_app(self):
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

def main():
    cb_hal = hal.HardwareAbstractionLayer(debug=True)
    nt = ntal.NetworkTableAbstractionLayer(address=ADDRESS, hal=cb_hal)
    app = wx.App()
    frame = MainWindow(hal=cb_hal, nt=nt)
    cb_hal.set_event_handler(frame.event_responder)
    cb_hal.start()
    app.Show()
    app.MainLoop()
    cb_hal.stop()

if __name__ == '__main__':
    main()
