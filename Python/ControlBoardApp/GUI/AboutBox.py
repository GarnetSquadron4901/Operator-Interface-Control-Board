import logging

import wx
import sys
import os
import networktables.version as ntver

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp import version as ntcbaver
    from ControlBoardApp.ControlBoardApp import APP_NAME
else:
    # Test Mode
    import version as ntcbaver
    from ControlBoardApp import APP_NAME

# HTML for the about box
ABOUT_TEXT = \
    """
    <p>%(app)s: %(cbaver)s</p>
    <p>pynetworktables: %(ntver)s</p>
    <p>wxPython: %(wxpy)s</p>
    <p>Python: %(python)s</p>
    <p>See <a href="http://github.com/GarnetSquardon4901/Operator-Interface-Control-Board">%(app)s Documentation</a></p>
    """


class HtmlAboutWindow(wx.html.HtmlWindow):
    def __init__(self, parent, wx_id, size=(600, 400)):
        """
        The About window is shown as an HTML page.
        :param parent: wx parent
        :param wx_id: wx id
        :param size: window size
        """
        wx.html.HtmlWindow.__init__(self, parent, wx_id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
        self.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnLinkClicked)

    @staticmethod
    def OnLinkClicked(event):
        """
        Method called if the user clicks the HTML link. 
        :param event: 
        :return: 
        """
        os.startfile(event.GetLinkInfo().GetHref())


class AboutBox(wx.Dialog):
    def __init__(self):
        """
        About Box Dialog
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('Displaying About Box')
        wx.Dialog.__init__(self,
                           None,
                           -1,
                           "About %s" % APP_NAME,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)
        hwin = HtmlAboutWindow(self, -1, size=(400, 200))
        vers = {"app": APP_NAME,
                "python": sys.version.split()[0],
                "wxpy": wx.VERSION_STRING,
                "cbaver": str(ntcbaver.__version__),
                "ntver": str(ntver.__version__)
                }
        hwin.SetPage(ABOUT_TEXT % vers)
        # btn = hwin.FindWindowById(wx.ID_OK)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth() + 25, irep.GetHeight() + 10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()
