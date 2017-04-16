import logging
import sys
import time
import wx
import wx.lib.agw.hypertreelist as HTL

logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.cbhal.ControlBoardBase import ControlBoardBase, ConnectionFailed
else:
    # Test Mode
    from cbhal.ControlBoardBase import ControlBoardBase, ConnectionFailed


class SimulatorBase(ControlBoardBase):
    """ Simulator base class for using a simulated control board"""

    def __init__(self):
        super(SimulatorBase, self).__init__()
        self.connected = False
        self.sim = None

    def set_sim_connection(self, sim):
        """
        Sets the simulation wx Frame connection
        :param sim: 
        :return: 
        """
        self.sim = sim

    def reset_board(self):
        """ Simulates a board reset. """
        logger.debug('Simulating a board reset')
        time.sleep(1)

    def is_connected(self):
        """ Returns if the simulator is in a connected state. """
        if self.sim is not None:
            return self.connected and self.sim.is_connected()
        else:
            return False

    def is_simulator(self):
        """ Returns True for all simulators.
        
        :return bool - True
        """
        return True

    def update(self):
        """
        Updates the simulator with output data. Receives a response packet with input data.
        :return: 
        """
        if not self.is_connected():
            raise ConnectionFailed('The simulator connection status is False.')

        # Check that there is a simulator frame connected
        if self.sim is not None:
            # Write outputs
            self.sim.set_pwms(self.getPwmValues())
            self.sim.set_leds(self.getLedValues())

            # Update screen
            self.sim.update_indicators()
            # CPU Saver - This is the only bound on how fast the simulator updates.
            time.sleep(20e-3)

            # Get inputs
            self.putAnalogvalues(self.sim.get_analogs())
            self.putSwitchvalues(self.sim.get_switches())
        else:
            raise ConnectionFailed('The simulator is not running yet.')

    def reconnect(self):
        """
        Simulates a board reconnection. 
        :return: 
        """
        self.disconnect()
        time.sleep(1)
        if self.sim is not None:
            if not self.sim.is_connected():
                raise ConnectionFailed('The simulated connection status is False.')
            else:
                logger.debug('Simulating a board connect')
                self.connected = True
        else:
            raise ConnectionFailed('The simulator is not running yet.')

    def disconnect(self):
        """
        Simulates a board disconnect.
        :return: 
        """
        if self.connected:
            logger.debug('Simulating a board disconnect')
            self.connected = False


class SimulatorFrame(wx.Frame):
    """
    wxPython frame used to show the simulator on your screen
    """

    DEFAULT_STATUS = '-                           '
    LED_ON = (0, 160, 0)  # Dark Green
    LED_OFF = (160, 0, 0)  # Dark Red

    def __init__(self, parent, hal, title):
        """
            wxPython frame used to show the simulator on your screen

        :param parent: wx Main Window
        :param hal: CBHAL instance
        :param title: Title to give the simulator
        """
        self.parent = parent
        self.hal = hal
        wx.Frame.__init__(self,
                          parent=parent,
                          title=title,
                          style=wx.DEFAULT_FRAME_STYLE & (~wx.CLOSE_BOX))

        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

        ##########################################
        # Setup the Hyper Tree List
        #
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
            item = wx.Slider(self)
            item.SetMin(0)
            item.SetMax(255)
            self.ANA_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.SW_Status = []
        for array_index in range(self.hal.SWITCH_INPUTS):
            label = self.tree.AppendItem(self.switch_status, 'SW ' + str(array_index))
            item = wx.CheckBox(self)
            self.SW_Status.append(item)
            self.tree.SetItemWindow(label, item, 1)

        self.analogs_out = [0] * self.hal.ANALOG_INPUTS
        self.switches_out = [False] * self.hal.SWITCH_INPUTS
        self.pwm_in = [0] * self.hal.PWM_OUTPUTS
        self.led_in = [False] * self.hal.LED_OUTPUTS

        self.tree.CalculateAndSetHeaderHeight()
        self.tree.DoHeaderLayout()
        self.tree.SetColumnWidth(0, self.tree.DoGetBestSize().GetWidth())
        #
        # Done setting up the Hyper Tree List
        ##########################################

        self.v_sizer.Add(self.tree, 1, wx.EXPAND, 0)
        self.tree.InvalidateBestSize()
        self.v_sizer.SetMinSize(self.tree.GetBestSize())

        self.SetAutoLayout(True)
        self.SetSizer(self.v_sizer)
        self.Layout()

        self.Refresh()

    def set_pwms(self, pwms):
        """
        Sets the PWM output list
        
        :param pwms: list(int)
        :return: 
        """
        self.pwm_in = pwms

    def set_leds(self, leds):
        """
        Sets the LED output list
        
        :param leds: list(bool)
        :return: 
        """
        self.led_in = leds

    def get_analogs(self):
        """
        Returns the Analog input list
        
        :return: list(int)
        """
        return self.analogs_out

    def get_switches(self):
        """
        Returns the Switch input list
    
        :return: list(bool) 
        """
        return self.switches_out

    def is_connected(self):
        """
        Returns if the "Is Connecte" checkbox is checked.
        :return: bool
        """
        return self.connection_status.GetValue()

    @staticmethod
    def put_tree_data(gui_element, status):
        """ Only updates tree data if new.
        :param gui_element: wxLabel object 
        :param status: str - new status
        """
        if gui_element.GetLabelText() != str(status):
            gui_element.SetLabelText(str(status))
            return True
        else:
            return False

    def _update_indicators(self):
        """
        Update the tree.
        :return: 
        """
        for channel in range(self.hal.LED_OUTPUTS):
            if self.put_tree_data(self.LED_Status[channel], ('On' if self.led_in[channel] else 'Off')):
                self.LED_Status[channel].SetForegroundColour(self.LED_ON if self.led_in[channel] else self.LED_OFF)

        for channel in range(self.hal.PWM_OUTPUTS):
            self.put_tree_data(self.PWM_Status[channel], self.pwm_in[channel])

        self.analogs_out = [analog.GetValue() for analog in self.ANA_Status]
        self.switches_out = [switch.GetValue() for switch in self.SW_Status]

    def update_indicators(self):
        """
        Thread safe tree update.
        :return: 
        """
        return wx.CallAfter(self._update_indicators)
