import wx
import HAL

class GarnetControlsGui(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='Garnet Controls')

        self.hal = HAL.HAL(debug=True)

        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

        led_v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.LED_Status = []
        for array_index in range(self.hal.LED_OUTPUTS):
            h_sizer = wx.BoxSizer()
            h_sizer.Add(wx.StaticText(self, label='LED ' + str(array_index) + ':\t'), wx.EXPAND)
            self.LED_Status.append(wx.StaticText(self, label=str(self.hal.led_out[array_index])))
            h_sizer.Add(self.LED_Status[-1], wx.EXPAND)
            led_v_sizer.Add(h_sizer, wx.EXPAND)

        pwm_v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.PWM_Status = []
        for array_index in range(self.hal.PWM_OUTPUTS):
            h_sizer = wx.BoxSizer()
            h_sizer.Add(wx.StaticText(self, label='PWM ' + str(array_index) + ':\t'), wx.EXPAND)
            self.PWM_Status.append(wx.StaticText(self, label=str(self.hal.pwm_out[array_index])))
            h_sizer.Add(self.PWM_Status[-1], wx.EXPAND)
            pwm_v_sizer.Add(h_sizer, wx.EXPAND)

        ana_v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.ANA_Status = []
        for array_index in range(self.hal.ANALOG_INPUTS):
            h_sizer = wx.BoxSizer()
            h_sizer.Add(wx.StaticText(self, label='ANA ' + str(array_index) + ':\t'), wx.EXPAND)
            self.ANA_Status.append(wx.StaticText(self, label=str(self.hal.analog_in[array_index])))
            h_sizer.Add(self.ANA_Status[-1], wx.EXPAND)
            ana_v_sizer.Add(h_sizer, wx.EXPAND)

        sw_v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SW_Status = []
        for array_index in range(self.hal.SWITCH_INPUTS):
            h_sizer = wx.BoxSizer()
            h_sizer.Add(wx.StaticText(self, label='SW ' + str(array_index) + ':\t'), wx.EXPAND)
            self.SW_Status.append(wx.StaticText(self, label=str(self.hal.switch_in[array_index])))
            h_sizer.Add(self.SW_Status[-1], wx.EXPAND)
            sw_v_sizer.Add(h_sizer, wx.EXPAND)

        self.v_sizer.Add(led_v_sizer, wx.EXPAND)
        self.v_sizer.Add(pwm_v_sizer, wx.EXPAND)
        self.v_sizer.Add(ana_v_sizer, wx.EXPAND)
        self.v_sizer.Add(sw_v_sizer, wx.EXPAND)

        self.SetSizer(self.v_sizer)
        self.DoGetBestSize()
        self.SetAutoLayout(True)


        self.hal.set_event_handler(self.update_indicators)

        self.hal.start()

    def update_indicators(self):
        for array_index in range(self.hal.LED_OUTPUTS):
            self.LED_Status[array_index].SetLabel(str(self.hal.led_out[array_index]))

        for array_index in range(self.hal.PWM_OUTPUTS):
            self.PWM_Status[array_index].SetLabel(str(self.hal.pwm_out[array_index]))

        for array_index in range(self.hal.ANALOG_INPUTS):
            self.ANA_Status[array_index].SetLabel(str(self.hal.analog_in[array_index]))

        for array_index in range(self.hal.SWITCH_INPUTS):
            self.SW_Status[array_index].SetLabel(str(self.hal.switch_in[array_index]))

        self.Update()










if __name__ == '__main__':
    app = wx.App()
    frame = GarnetControlsGui()
    frame.Show()
    app.MainLoop()
    frame.hal.stop()