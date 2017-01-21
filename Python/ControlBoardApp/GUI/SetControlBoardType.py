import logging

logger = logging.getLogger(__name__)

from ControlBoardApp.cbhal import cbtypes

import wx

class SetControlBoardBox(wx.Dialog):

    def __init__(self, parent, current_cb_type):
        super(SetControlBoardBox, self).__init__(parent=parent, title="Set Control Board Type")

        panel = wx.Panel(self)

        self.choice_keys = list(cbtypes.keys())
        self.choices = [cbtypes[cbkey]['name'] for cbkey in self.choice_keys]
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
        logger.info('Okay button pressed')
        self.ok_pressed = True
        self.OnClose()

    def OnClose(self, _=None):
        logger.info('Closing window')
        self.Destroy()

    def wasOkPressed(self):
        return self.ok_pressed

    def get_cb_type_sel(self):
        return self.choice_keys[self.conn_type_sel.GetSelection()]

    def get_cb_type_name(self):
        return self.choices[self.conn_type_sel.GetSelection()]
