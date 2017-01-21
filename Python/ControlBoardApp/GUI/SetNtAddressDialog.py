import wx
import string
import logging

logger = logging.getLogger(__name__)

class TeamNumberValidator(wx.Validator):
    def __init__(self):
        super(TeamNumberValidator, self).__init__()
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return TeamNumberValidator()

    def ValidateMdns(self):
        tc = self.GetWindow()
        val = tc.GetValue()

        for x in val:
            # Make sure it's a number. Mdns can accept higher than team values than 9999
            if x not in string.digits:
                logger.debug('The team number contains non-numeric characters')
                return False

        if len(val) < 1:
            logger.debug('The team number input cannot be empty')
            return False

        if int(val) < 1:
            logger.debug('The team number must be greater than 0')
            return False

        logger.debug('The team number is valid')
        return True

    def ValidateIpv4(self):
        tc = self.GetWindow()
        val = tc.GetValue()

        for x in val:
            # Make sure it's a number. Mdns can accept higher than team values than 9999
            if x not in string.digits:
                logger.debug('The team number contains non-numeric characters')
                return False

        if len(val) < 1:
            logger.debug('The team number input cannot be empty')
            return False

        if int(val) < 1 or int(val) > 9999:
            logger.debug('%s is not a valid team number' % val)
            return False

        logger.debug('The team number is valid')
        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            logger.debug('Key valid, passing it to the TextCtrl')
            event.Skip()
            return

        if chr(key) in string.digits:
            logger.debug('Character valid, passing it to the TextCtrl')
            event.Skip()
            return

        # Returning without calling event.Skip eats the event before it
        # gets to the text control
        logger.debug('Invalid character: %s(%d)' % (chr(key), key))
        return

    def TransferToWindow(self):
        """ Transfer data from validator to window.

            The default implementation returns False, indicating that an error
            occurred.  We simply return True, as we don't do any data transfer.
        """
        return True # Prevent wxDialog from complaining.

class SetAddressBox(wx.Dialog):

    CURRENT='Current'
    SIMULATOR='Simulator'
    MDNS='>=2015 mDNS Address'
    IPV4='<=2014 IPv4 Address'
    MANUAL='Manually set the address'

    def __init__(self, parent, current_address):
        super(SetAddressBox, self).__init__(parent=parent, title="Set NT Server Address")

        self.current_address = current_address

        panel = wx.Panel(self, )
        hbox_final_address = wx.BoxSizer(wx.HORIZONTAL)

        self.address_input = wx.TextCtrl(self, id=wx.ID_ANY, value='')

        hbox_final_address.Add(wx.StaticText(self, id=wx.ID_ANY, label='Address:'),
                                flag = wx.EXPAND,
                                border = 5,
                                proportion = 0)
        hbox_final_address.Add(self.address_input,
                               flag = wx.EXPAND,
                               border = 5,
                               proportion = 1)

        hbox_quick_set = wx.BoxSizer(wx.HORIZONTAL)

        self.choices=[self.CURRENT, self.MDNS, self.IPV4, self.SIMULATOR, self.MANUAL]
        self.conn_type_sel = wx.RadioBox(parent=self,
                                         id=wx.ID_ANY,
                                         label='Connection Type',
                                         choices=self.choices,
                                         style=wx.VERTICAL
                                         )
        self.conn_type_sel.SetSelection(self.choices.index(self.CURRENT))
        self.conn_type_sel.Bind(wx.EVT_RADIOBOX, self.OnConnTypeSelChanged)



        self.teamNumberInput = wx.TextCtrl(self, id=wx.ID_ANY, validator=TeamNumberValidator())
        self.teamNumberInput.Bind(wx.EVT_TEXT, self.OnConnTypeSelChanged)

        hbox_quick_set.Add(self.conn_type_sel, flag=wx.ALL | wx.EXPAND, border=10)

        team_num_input_sizer = wx.BoxSizer(wx.VERTICAL)
        team_num_input_sizer.Add(wx.StaticText(self, id=wx.ID_ANY, label="Team Number:"), flag=wx.ALL | wx.ALIGN_LEFT)
        team_num_input_sizer.Add(self.teamNumberInput, flag=wx.ALL | wx.ALIGN_LEFT)
        hbox_quick_set.Add(team_num_input_sizer, border=10)


        hbox_action_buttons = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox_action_buttons.Add(okButton)
        hbox_action_buttons.Add(closeButton, flag=wx.LEFT, border=5)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, id=wx.ID_ANY, label='Use the buttons below or manually type the address to set the address of the Network Table server.'), flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(panel, flag=wx.ALL | wx.EXPAND, border=0)
        vbox.Add(hbox_quick_set, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox_final_address, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, border=5)
        vbox.Add(hbox_action_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)
        vbox.Fit(self)
        self.SetAutoLayout(True)
        self.Layout()

        okButton.Bind(wx.EVT_BUTTON, self.OnOkClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

        self.ok_pressed = False

        self.OnConnTypeSelChanged()

        if self.current_address is None:
            self.OnSimulatorSetAddress()
        else:
            self.OnCurrentButtonPressed()

    def OnConnTypeSelChanged(self, _=None):
        choice = self.choices[self.conn_type_sel.GetSelection()]
        logger.info('Connection type selector changed: %s' % choice)
        if choice == self.CURRENT:
            self.OnCurrentButtonPressed()
            self.teamNumberInput.Enable(False)
            self.address_input.Enable(False)
        elif choice == self.MDNS:
            self.OnMdnsSetAddress()
            self.teamNumberInput.Enable(True)
            self.address_input.Enable(False)
        elif choice == self.IPV4:
            self.OnIpv4SetAddress()
            self.teamNumberInput.Enable(True)
            self.address_input.Enable(False)
        elif choice == self.SIMULATOR:
            self.OnSimulatorSetAddress()
            self.teamNumberInput.Enable(False)
            self.address_input.Enable(False)
        elif choice == self.MANUAL:
            self.teamNumberInput.Enable(False)
            self.address_input.Enable(True)
        else:
            self.OnCurrentButtonPressed()
            self.teamNumberInput.Enable(False)
            self.address_input.Enable(False)

    def OnCurrentButtonPressed(self):
        logger.info('Current config selected')
        self.setAddress(self.current_address)

    def OnSimulatorSetAddress(self):
        logger.info('Simulator selected')
        self.setAddress('localhost')

    def OnMdnsSetAddress(self):
        logger.info('MDNS (>2015) selected')
        if self.teamNumberInput.GetValidator().ValidateMdns():
            self.setAddress('roborio-%d-frc.local' % int(self.teamNumberInput.GetValue()))

    def OnIpv4SetAddress(self):
        logger.info("IPV4 (<=2015) selected")
        if self.teamNumberInput.GetValidator().ValidateIpv4():
            teamNumStr = '%04d' % int(self.teamNumberInput.GetValue())
            self.setAddress('10.%d.%d.5' % (int(teamNumStr[0:2]), int(teamNumStr[2:4])))

    def setAddress(self, address):
        logger.info('Return address is now: %s' % address)
        self.address_input.SetValue(address)

    def OnOkClose(self, _=None):
        logger.info('Okay button pressed')
        self.ok_pressed = True
        self.OnClose()

    def OnClose(self, _=None):
        logger.info('Closing window')
        self.Destroy()

    def okPressed(self):
        return self.ok_pressed

    def getAddress(self):
        return self.address_input.GetValue()
