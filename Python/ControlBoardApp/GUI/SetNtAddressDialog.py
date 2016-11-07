import wx

class SetAddressBox(wx.Dialog):

    CURRENT='Current'
    SIMULATOR='Simulator'
    MDNS='>=2015 mDNS Address'
    IPV4='<=2014 IPv4 Address'
    MANUAL='Manually set the address'

    def __init__(self, parent, current_address):
        super(SetAddressBox, self).__init__(parent=parent, title="Set NT Server Address")

        self.current_address = current_address

        panel = wx.Panel(self)
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


        # simButton = wx.Button(self,   label='Simulator Address')
        # simButton.Bind(wx.EVT_BUTTON, self.OnSimulatorButtonPressed)


        # self.default_radio_btn = wx.RadioButton(parent=self, id=wx.ID_ANY)
        self.choices=[self.CURRENT, self.MDNS, self.IPV4, self.SIMULATOR, self.MANUAL]
        self.conn_type_sel = wx.RadioBox(parent=self,
                                         id=wx.ID_ANY,
                                         label='Connection Type',
                                         choices=self.choices,
                                         style=wx.VERTICAL
                                         )
        self.conn_type_sel.SetSelection(self.choices.index(self.CURRENT))
        self.conn_type_sel.Bind(wx.EVT_RADIOBOX, self.OnConnTypeSelChanged)


        self.teamNumberInput = wx.TextCtrl(self, id=wx.ID_ANY)
        # newCsButton = wx.Button(self, label='>=2015 mDNS Address')
        # newCsButton.Bind(wx.EVT_BUTTON, self.OnNewCsButtonPressed)
        # oldCsButton = wx.Button(self, label='<=2014 IPv4 Address')
        # oldCsButton.Bind(wx.EVT_BUTTON, self.OnOldCsButtonPressed)
        # hbox_quick_set.Add(simButton, wx.ALL | wx.EXPAND, 20)
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
        self.SetAutoLayout(True)
        self.Layout()

        okButton.Bind(wx.EVT_BUTTON, self.OnOkClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

        self.ok_pressed = False

        if self.current_address is None:
            self.OnSimulatorSetAddress()
        else:
            self.OnCurrentButtonPressed()

    def OnConnTypeSelChanged(self, event):
        choice = self.choices[event.GetSelection()]
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
        self.setAddress(self.current_address)

    def OnSimulatorSetAddress(self):
        self.setAddress('localhost')

    def OnMdnsSetAddress(self):
        self.setAddress('roborio-%s-frc.local' % self.teamNumberInput.GetValue())

    def OnIpv4SetAddress(self):
        teamNumStr = '%04d' % int(self.teamNumberInput.GetValue())
        self.setAddress('10.%d.%d.5' % (int(teamNumStr[0:2]), int(teamNumStr[2:4])))

    def setAddress(self, address):
        self.address_input.SetValue(address)

    def OnOkClose(self, _=None):
        self.ok_pressed = True
        self.OnClose()

    def OnClose(self, _=None):
        self.Destroy()

    def okPressed(self):
        return self.ok_pressed

    def getAddress(self):
        return self.address_input.GetValue()
