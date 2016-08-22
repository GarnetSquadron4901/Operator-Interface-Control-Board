import wx
import wx.lib.agw.hypertreelist as HTL
import time

from ControlBoardApp import hal
from ControlBoardApp import ntal
from threading import Event, Thread

ADDRESS = 'localhost'

class MainWindow(wx.Frame):

    DEFAULT_STATUS = '-                         '

    def __init__(self, hal, nt):
        wx.Frame.__init__(self, None, title='Garnet Controls')

        self.hal = hal
        self.nt = nt

        # self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
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
        # self.v_sizer.Fit(self)
        # self.v_sizer.SetMinSize(self.tree.DoGetBestSize())
        # self.SetSize(self.tree.DoGetBestSize())
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
