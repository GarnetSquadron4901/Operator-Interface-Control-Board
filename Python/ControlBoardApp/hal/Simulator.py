import time
import wx
import wx.lib.agw.hypertreelist as HTL


from ControlBoardApp.hal.ControlBoardBase import ControlBoardBase, ConnectionFailed


class HardwareAbstractionLayer(ControlBoardBase):

    LED_OUTPUTS = 16
    PWM_OUTPUTS = 11
    ANALOG_INPUTS = 16
    SWITCH_INPUTS = 16

    NAME = 'Control Board Simulator'

    def __init__(self, debug):

        self.connected = False

        super(HardwareAbstractionLayer, self).__init__(debug)

        self.sim = None

    def set_sim_connection(self, sim):
        self.sim = sim

    def reset_board(self):
        time.sleep(1)

    def is_connected(self):
        if self.sim is not None:
            return self.connected and self.sim.is_connected()
        else:
            return False

    def is_simulator(self):
        return True

    def update(self):

        if self.sim is not None:
            pwms = self.getPwmValues()
            leds = self.getLedValues()

            # Update screen

            self.sim.update_indicators(pwms=pwms, leds=leds, )
            time.sleep(20e-3)

            self.putAnalogvalues(analogs)
            self.putSwitchvalues(switches)
        else:
            raise ConnectionFailed('The simulator is not running yet.')

    def reconnect(self):
        self.disconnect()
        time.sleep(1)
        if self.sim is not None:
            if not self.sim.is_connected():
                raise ConnectionFailed('The simulated connection status is False.')
            else:
                self.connected = True
        else:
            raise ConnectionFailed('The simulator is not running yet.')

    def disconnect(self):
        self.connected = False

class SimulatorFrame(wx.Frame):

    DEFAULT_STATUS = '-                           '

    def __init__(self, parent, hal):
        self.parent = parent
        self.hal = hal
        wx.Frame.__init__(self,
                          parent=parent,
                          title='Simulator',
                          style=wx.DEFAULT_FRAME_STYLE & (~wx.CLOSE_BOX))

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

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'Control Board Connected?')
        self.connection_status = wx.CheckBox(self)
        self.connection_status.SetValue(True)
        self.tree.SetItemWindow(label, self.connection_status, 1)

        self.analog_status = self.tree.AppendItem(self.tree.GetRootItem(), 'Analog Inputs')
        self.led_status = self.tree.AppendItem(self.tree.GetRootItem(), 'LED Outputs')
        self.pwm_status = self.tree.AppendItem(self.tree.GetRootItem(), 'PWM Outputs')
        self.switch_status = self.tree.AppendItem(self.tree.GetRootItem(), 'Switch Inputs')

        self.LED_Status = []
        for array_index in range(self.hal.LED_OUTPUTS):
            label = self.tree.AppendItem(self.led_status, 'LED ' + str(array_index))
            item = wx.CheckBox(self)
            item.Disable()
            item.SetValue(False)
            self.LED_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.PWM_Status = []
        for array_index in range(self.hal.PWM_OUTPUTS):
            label = self.tree.AppendItem(self.pwm_status, 'PWM ' + str(array_index))
            item = wx.StaticText(self, label=self.DEFAULT_STATUS)
            self.PWM_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.ANA_Status = []
        self.analogs_out = []
        for array_index in range(self.hal.ANALOG_INPUTS):
            label = self.tree.AppendItem(self.analog_status, 'ANA ' + str(array_index))
            item = wx.Slider(self)
            item.SetMin(0)
            item.SetMax(255)
            self.ANA_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.SW_Status = []
        self.switches_out = []
        for array_index in range(self.hal.SWITCH_INPUTS):
            label = self.tree.AppendItem(self.switch_status, 'SW ' + str(array_index))
            item = wx.CheckBox(self)
            self.SW_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)


        self.tree.CalculateAndSetHeaderHeight()
        self.tree.DoHeaderLayout()
        self.tree.SetColumnWidth(0, self.tree.DoGetBestSize().GetWidth())


        self.v_sizer.Add(self.tree, 1, wx.EXPAND, 0)
        self.tree.InvalidateBestSize()
        self.v_sizer.SetMinSize(self.tree.GetBestSize())

        self.SetAutoLayout(True)
        self.SetSizer(self.v_sizer)
        self.Layout()

    def is_connected(self):
        return self.connection_status.GetValue()

    def put_tree_data(self, gui_element, status):
        if gui_element.GetLabelText() != str(status):
            gui_element.SetLabelText(str(status))

    def _update_indicators(self, pwms, leds):

        for channel in range(self.hal.LED_OUTPUTS):
            self.put_tree_data(self.LED_Status[channel], leds[channel])

        for channel in range(self.hal.PWM_OUTPUTS):
            self.put_tree_data(self.PWM_Status[channel], pwms[channel])

        self.analogs_out = [analog.GetValue() for analog in self.ANA_Status]
        self.switches_out = [switch.GetValue() for switch in self.SW_Status]


    def update_indicators(self, pwms, leds):
        return wx.CallAfter(self._update_indicators, pwms, leds)