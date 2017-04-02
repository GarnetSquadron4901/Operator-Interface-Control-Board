import logging

import wx
import sys
import os
import networktables.version as ntver

from ControlBoardApp import _version as ntcbaver


class HtmlAboutWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnLinkClicked)

    def OnLinkClicked(self, event):
        os.startfile(event.GetLinkInfo().GetHref())

aboutText = """<p>FRC Control Board Application: %(cbaver)s</p>
<p>pynetworktables: %(ntver)s</p>
<p>wxPython: %(wxpy)s</p>
<p>Python: %(python)s</p>
<p>See <a href="http://github.com/GarnetSquardon4901/Operator-Interface-Control-Board">FRC Control Board Documentation</a></p>
"""
class AboutBox(wx.Dialog):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.logger.info('Displaying About Box')
        wx.Dialog.__init__(self,
                           None,
                           -1,
                           "About FRC Control Board",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)
        hwin = HtmlAboutWindow(self, -1, size=(400, 200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        vers["cbaver"] = str(ntcbaver.__version__)
        vers["ntver"] = str(ntver.__version__)
        hwin.SetPage(aboutText % vers)
        # btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()
