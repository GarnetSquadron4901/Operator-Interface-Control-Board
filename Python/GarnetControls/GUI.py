import wx
import HAL
import GarnetControlsNT
import time
from threading import Event, Thread

address = 'localhost'

class GarnetControlsGui(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='Garnet Controls')

        self.hal = HAL.HAL(debug=True)
        self.nt = GarnetControlsNT.GarnetControlsNT(address=address, hal=self.hal)


        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

        update_rate_v_sizer = wx.BoxSizer(wx.VERTICAL)
        h_sizer = wx.BoxSizer()
        h_sizer.Add(wx.StaticText(self, label='Control Board Status:\t'))
        self.update_rate_status = wx.StaticText(self, label='-                                                       ')
        h_sizer.Add(self.update_rate_status)
        update_rate_v_sizer.Add(h_sizer, wx.EXPAND)

        led_v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.LED_Status = []
        for array_index in range(self.hal.LED_OUTPUTS):
            h_sizer = wx.BoxSizer()
            h_sizer.Add(wx.StaticText(self, label='LED ' + str(array_index) + ':\t'), wx.EXPAND)
            self.LED_Status.append(wx.StaticText(self, label='-'))
            h_sizer.Add(self.LED_Status[-1], wx.EXPAND)
            led_v_sizer.Add(h_sizer, wx.EXPAND)

        pwm_v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.PWM_Status = []
        for array_index in range(self.hal.PWM_OUTPUTS):
            h_sizer = wx.BoxSizer()
            h_sizer.Add(wx.StaticText(self, label='PWM ' + str(array_index) + ':\t'), wx.EXPAND)
            self.PWM_Status.append(wx.StaticText(self, label='-'))
            h_sizer.Add(self.PWM_Status[-1], wx.EXPAND)
            pwm_v_sizer.Add(h_sizer, wx.EXPAND)

        ana_v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.ANA_Status = []
        for array_index in range(self.hal.ANALOG_INPUTS):
            h_sizer = wx.BoxSizer()
            h_sizer.Add(wx.StaticText(self, label='ANA ' + str(array_index) + ':\t'), wx.EXPAND)
            self.ANA_Status.append(wx.StaticText(self, label='-'))
            h_sizer.Add(self.ANA_Status[-1], wx.EXPAND)
            ana_v_sizer.Add(h_sizer, wx.EXPAND)

        sw_v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SW_Status = []
        for array_index in range(self.hal.SWITCH_INPUTS):
            h_sizer = wx.BoxSizer()
            h_sizer.Add(wx.StaticText(self, label='SW ' + str(array_index) + ':\t'), wx.EXPAND)
            self.SW_Status.append(wx.StaticText(self, label='-'))
            h_sizer.Add(self.SW_Status[-1], wx.EXPAND)
            sw_v_sizer.Add(h_sizer, wx.EXPAND)

        self.v_sizer.Add(update_rate_v_sizer)
        self.v_sizer.Add(led_v_sizer)
        self.v_sizer.Add(pwm_v_sizer)
        self.v_sizer.Add(ana_v_sizer)
        self.v_sizer.Add(sw_v_sizer)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.is_running = True

        self.gui_update_trigger = Event()
        self.hal.set_event_handler(self.event_responder)
        self.hal.start()

        self.event_wait_loop_thread = Thread(target=self.gui_update_loop)
        self.event_wait_loop_thread.start()

        self.SetSizerAndFit(self.v_sizer)
        self.DoGetBestSize()
        self.SetAutoLayout(True)


    def event_responder(self):
        self.gui_update_trigger.set()
        self.nt.update()

    def gui_update_loop(self):
        while self.is_running:
            self.gui_update_trigger.wait(0.5)
            self.gui_update_trigger.clear()
            if self.hal.usb_connected():
                self.update_indicators()

    def on_close(self, event):
        print ('Stopping HAL thread')
        self.hal.stop()

        print('Stopping GUI refresh thread')
        self.is_running = False
        self.event_wait_loop_thread.join()

        self.Hide()
        self.Destroy()

    def get_control_board_status(self):

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

    def update_gui_status(self, gui_element, status):
        if gui_element.GetLabelText() != str(status):
            gui_element.SetLabelText(str(status))

    def update_indicators(self):

        self.update_gui_status(self.update_rate_status, self.get_control_board_status())

        if self.hal.is_control_board_running():

            for channel in range(self.hal.LED_OUTPUTS):
                self.update_gui_status(self.LED_Status[channel], self.get_led_status(channel))

            for channel in range(self.hal.PWM_OUTPUTS):
                self.update_gui_status(self.PWM_Status[channel], self.get_pwm_status(channel))

            for channel in range(self.hal.ANALOG_INPUTS):
                self.update_gui_status(self.ANA_Status[channel], self.get_ana_status(channel))

            for channel in range(self.hal.SWITCH_INPUTS):
                self.update_gui_status(self.SW_Status[channel], self.get_sw_status(channel))
        else:

            for channel in range(self.hal.LED_OUTPUTS):
                self.update_gui_status(self.LED_Status[channel], '-')

            for channel in range(self.hal.PWM_OUTPUTS):
                self.update_gui_status(self.PWM_Status[channel], '-')

            for channel in range(self.hal.ANALOG_INPUTS):
                self.update_gui_status(self.ANA_Status[channel], '-')

            for channel in range(self.hal.SWITCH_INPUTS):
                self.update_gui_status(self.SW_Status[channel], '-')

            self.Update()


if __name__ == '__main__':
    app = wx.App()
    frame = GarnetControlsGui()
    frame.Show()
    app.MainLoop()
