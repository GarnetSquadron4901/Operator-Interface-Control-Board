import wx
import logging

logger = logging.getLogger(__name__)

class ConfigFile:
    def __init__(self, filename):
        wx.LogVerbose('Loading config: %s' % filename)
        pass

    def get_nt_server_address(self):
        nt_address = 'localhost'

        wx.LogVerbose('Loaded NT server address from config: %s' % nt_address)
        return nt_address

    def set_nt_server_address(self, nt_address):
        wx.LogVerbose('Saving NT server address to config: %s' % nt_address)

    def get_cb_type(self):
        cb_type = 'Simulator'
        wx.LogVerbose('Loaded control board type from config: %s' % cb_type)

    def set_cb_type(self, cb_type):
        wx.LogVerbose('Saving control board type to config: %s' % cb_type)


