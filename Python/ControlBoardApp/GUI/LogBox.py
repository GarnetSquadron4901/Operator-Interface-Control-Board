import logging
import logging.config
import wx


########################################################################
class CustomConsoleHandler(logging.StreamHandler):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, textctrl):
        """"""
        logging.StreamHandler.__init__(self)
        self.textctrl = textctrl

    # ----------------------------------------------------------------------
    def emit(self, record):
        """Constructor"""
        msg = self.format(record)
        self.textctrl.WriteText(msg + "\n")
        self.flush()


########################################################################
class MyPanel(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.logger = logging.getLogger(__package__)

        logText = wx.TextCtrl(self,
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        btn = wx.Button(self, label="Press Me")
        btn.Bind(wx.EVT_BUTTON, self.onPress)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(logText, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn, 0, wx.ALL, 5)
        self.SetSizer(sizer)

        txtHandler = CustomConsoleHandler(logText)
        self.logger.addHandler(txtHandler)

    # ----------------------------------------------------------------------
    def onPress(self, event):
        """
        """
        self.logger.error("Error Will Robinson!")
        self.logger.info("Informational message")


########################################################################
class MyFrame(wx.Frame):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Logging test")
        panel = MyPanel(self)
        self.logger = logging.getLogger("wxApp")
        self.Show()