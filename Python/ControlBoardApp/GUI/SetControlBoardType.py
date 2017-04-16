import logging
import wx


class SetControlBoardBox(wx.Dialog):
    def __init__(self, parent, current_cb_type, cbhal_handler):
        """
        Set Control Board Dialog
        
        :param parent: wx parent
        :param current_cb_type: str - current control board type
        :param cbhal_handler: ControlBoardHalInterfaceHandler
        """
        super(SetControlBoardBox, self).__init__(parent=parent, title="Set Control Board Type")

        panel = wx.Panel(self)

        self.logger = logging.getLogger(__name__)

        self.choice_keys = cbhal_handler.get_keys()
        self.choices = [cbhal_handler.get_types()[cbkey]['name'] for cbkey in self.choice_keys]
        self.current_cb_type = self.choices[self.choice_keys.index(current_cb_type)]
        self.conn_type_sel = wx.RadioBox(parent=self,
                                         id=wx.ID_ANY,
                                         label='Control Board Type',
                                         choices=self.choices,
                                         style=wx.VERTICAL
                                         )
        self.conn_type_sel.SetSelection(self.choices.index(self.current_cb_type))

        hbox_quick_set = wx.BoxSizer(wx.HORIZONTAL)
        hbox_quick_set.Add(self.conn_type_sel, flag=wx.ALL | wx.EXPAND, border=10)

        hbox_action_buttons = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox_action_buttons.Add(okButton, flag=wx.ALL | wx.EXPAND, border=10)
        hbox_action_buttons.Add(closeButton, flag=wx.ALL | wx.EXPAND, border=10)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(panel, flag=wx.ALL | wx.EXPAND)
        vbox.Add(hbox_quick_set, flag=wx.ALL | wx.EXPAND)
        vbox.Add(hbox_action_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM)

        self.SetSizer(vbox)
        vbox.Fit(self)

        self.SetAutoLayout(True)
        self.Layout()

        okButton.Bind(wx.EVT_BUTTON, self.OnOkClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

        self.ok_pressed = False

    def OnOkClose(self, _=None):
        """
        Response to the Ok or Close button being pressed
        
        :param _: event - not used
        :return: 
        """
        self.logger.info('Okay button pressed')
        self.ok_pressed = True
        self.OnClose()

    def OnClose(self, _=None):
        """
        Response to the dialog closing.
        
        :param _: event - not used
        :return: 
        """
        self.logger.info('Closing window')
        self.Destroy()

    def wasOkPressed(self):
        """
        Indicates if the Ok button was pressed. 
        
        :return: bool - True if Ok was pressed
        """
        return self.ok_pressed

    def get_cb_type_sel(self):
        """
        Returns the control board type
        
        :return: str - CB_SNAME
        """
        return self.choice_keys[self.conn_type_sel.GetSelection()]

    def get_cb_type_name(self):
        """
        Returns the control board name
        
        :return: str - CB_LNAME
        """
        return self.choices[self.conn_type_sel.GetSelection()]
