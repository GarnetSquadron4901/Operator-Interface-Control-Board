import wx
import wx.lib.agw.hypertreelist as HTL
import time

from ControlBoardApp import hal
from ControlBoardApp import ntal
from threading import Event, Thread

ADDRESS = 'localhost'

class MainWindow(wx.Frame):
    def __init__(self, hal, nt):
        wx.Frame.__init__(self, None, title='Garnet Controls')

        self.hal = hal
        self.nt = nt

        # self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

        self.tree = HTL.HyperTreeList(self, style=wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.TR_HIDE_ROOT)
        self.tree.AddColumn('Name')
        self.tree.AddColumn('Status')
        self.tree.AddRoot('Root')
        self.tree.SetMainColumn(0)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'Control Board Status')
        self.hal_status = wx.StaticText(self, label='-')
        self.tree.SetItemWindow(label, self.hal_status, 1)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'Network Table')
        self.ntal_status = wx.StaticText(self, label='-')
        self.tree.SetItemWindow(label, self.ntal_status, 1)

        self.analog_status = self.tree.AppendItem(self.tree.GetRootItem(), 'Analog Inputs')
        self.led_status = self.tree.AppendItem(self.tree.GetRootItem(), 'LED Outputs')
        self.pwm_status = self.tree.AppendItem(self.tree.GetRootItem(), 'PWM Outputs')
        self.switch_status = self.tree.AppendItem(self.tree.GetRootItem(), 'Switch Inputs')



        self.LED_Status = []
        for array_index in range(self.hal.LED_OUTPUTS):
            label = self.tree.AppendItem(self.led_status, 'LED ' + str(array_index))
            item = wx.StaticText(self, label='-')
            self.LED_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)


        self.PWM_Status = []
        for array_index in range(self.hal.PWM_OUTPUTS):
            label = self.tree.AppendItem(self.pwm_status, 'PWM ' + str(array_index))
            item = wx.StaticText(self, label='-')
            self.PWM_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.ANA_Status = []
        for array_index in range(self.hal.ANALOG_INPUTS):
            label = self.tree.AppendItem(self.analog_status, 'ANA ' + str(array_index))
            item = wx.StaticText(self, label='-')
            self.ANA_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.SW_Status = []
        for array_index in range(self.hal.SWITCH_INPUTS):
            # h_sizer = wx.BoxSizer()
            label = self.tree.AppendItem(self.switch_status, 'SW ' + str(array_index))
            item = wx.StaticText(self, label='-')
            self.SW_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.v_sizer.Add(self.tree, 1, wx.EXPAND, 0)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.is_running = True

        self.gui_update_trigger = Event()
        self.hal.set_event_handler(self.event_responder)

        self.event_wait_loop_thread = Thread(target=self.gui_update_loop)
        self.event_wait_loop_thread.start()

        self.hal.start()

        self.SetSizer(self.v_sizer)
        self.v_sizer.Fit(self)
        self.v_sizer.SetSizeHints(self)
        self.SetAutoLayout(True)
        self.Layout()

    def event_responder(self):
        # self.gui_update_trigger.set()
        self.nt.update()

    def gui_update_loop(self):
        while self.is_running:
            # self.gui_update_trigger.wait(0.5)
            time.sleep(0.5)
            # self.gui_update_trigger.clear()
            self.update_indicators()

    def on_close(self, _):
        print ('Stopping HAL thread')
        self.hal.stop()

        print('Stopping GUI refresh thread')
        self.is_running = False
        self.event_wait_loop_thread.join()

        self.Hide()
        self.Destroy()

    def get_hal_status(self):

        if self.hal.is_control_board_running():
            rate = self.hal.getUpdateRate()
            if rate is not None:
                return 'Running, Updating @ ' + str(int(rate)) + ' Hz'
            else:
                return 'Running, Calculating update rate...'
        else:
            return self.hal.get_hal_state()

    def get_led_status(self, ch):
        return 'On' if self.hal.getLedValue(ch) else 'Off'

    def get_pwm_status(self, ch):
        return str(self.hal.getPwmValue(ch))

    def get_ana_status(self, ch):
        return str(self.hal.getAnalogValue(ch))

    def get_sw_status(self, ch):
        return 'Closed' if self.hal.getSwitchValue(ch) else 'Open'

    def update_tree_status(self, gui_element, status):
        if gui_element.GetLabelText() != str(status):
            gui_element.SetLabelText(str(status))

    def update_indicators(self):

        self.update_tree_status(self.hal_status, self.get_hal_status())
        self.update_tree_status(self.ntal_status, 'Connected' if self.nt.isConnected() else 'Disconnected')

        # if self.hal.is_control_board_running():
        #
        #     for channel in range(self.hal.LED_OUTPUTS):
        #         self.update_tree_status(self.LED_Status[channel], self.get_led_status(channel))
        #
        #     for channel in range(self.hal.PWM_OUTPUTS):
        #         self.update_tree_status(self.PWM_Status[channel], self.get_pwm_status(channel))
        #
        #     for channel in range(self.hal.ANALOG_INPUTS):
        #         self.update_tree_status(self.ANA_Status[channel], self.get_ana_status(channel))
        #
        #     for channel in range(self.hal.SWITCH_INPUTS):
        #         self.update_tree_status(self.SW_Status[channel], self.get_sw_status(channel))
        # else:
        #
        #     for channel in range(self.hal.LED_OUTPUTS):
        #         self.update_tree_status(self.LED_Status[channel], '-')
        #
        #     for channel in range(self.hal.PWM_OUTPUTS):
        #         self.update_tree_status(self.PWM_Status[channel], '-')
        #
        #     for channel in range(self.hal.ANALOG_INPUTS):
        #         self.update_tree_status(self.ANA_Status[channel], '-')
        #
        #     for channel in range(self.hal.SWITCH_INPUTS):
        #         self.update_tree_status(self.SW_Status[channel], '-')
        #
        #     self.Update()

def main():
    cb_hal = hal.HardwareAbstractionLayer(debug=True)
    nt = ntal.NetworkTableAbstractionLayer(address=ADDRESS, hal=cb_hal)
    app = wx.App()
    frame = MainWindow(hal=cb_hal, nt=nt)
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
