import logging
import wx, wx.html
import wx.lib.agw.hypertreelist as HTL
import ctypes
import os

from ControlBoardApp import LOG_PATH
from ControlBoardApp.GUI.SetNtAddressDialog import SetAddressBox
from ControlBoardApp.GUI.AboutBox import AboutBox
from ControlBoardApp.GUI.TaskBarIcon import TaskBarIcon
from ControlBoardApp.GUI.SetControlBoardType import SetControlBoardBox



# Main application icon
MAIN_ICON = os.path.abspath(os.path.join(os.path.split(__file__)[0], 'ControlBoard.ico'))

class MainWindow(wx.Frame):

    DEFAULT_STATUS = '-                           '
    ANALOG_LNAME = 'Analog Inputs'
    ANALOG_SNAME = 'ANA'
    SWITCH_LNAME = 'Switch Inputs'
    SWITCH_SNAME = 'SW'
    LEDS_LNAME = 'LED Outputs'
    LEDS_SNAME = 'LED'
    PWMS_LNAME = 'PWM Outputs'
    PWMS_SNAME = 'PWM'

    def __init__(self, cbhal_handler, nt, config):
        '''

        :param cbhal_handler: cbhal.ControlBoardBase
        :param nt: NetworkTableAbstractionLayer
        :param config: config.ConfigFile
        '''
        wx.Frame.__init__(self, None, title='FRC Control Board')

        self.logger = logging.getLogger(__name__)

        self.cbhal_handler = cbhal_handler
        self.nt = nt
        self.config = config

        self.log_window = wx.LogWindow(self, 'Control Board Log', False)

        # Set Icon
        # Setup the icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(MAIN_ICON, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        # Windows isn't smart enough to pull the right icon (it looks at the EXE), point it to look at this script's
        # icon
        # from http://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-
        # 7/1552105#1552105
        myappid = u'ControlBoardApp.1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Set Taskbar Icon
        self.tb_icon = TaskBarIcon(self)

        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

        ########################################
        # Menu bar configuration

        # File menu
        self.menu_file = wx.Menu()
        self.menu_file_hide = self.menu_file.Append(wx.ID_ANY, 'Hide', 'Hide this window. Application continues running in the background.')
        self.menu_file_quit = self.menu_file.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.hide_window, self.menu_file_hide)
        self.Bind(wx.EVT_MENU, self.exit_app, self.menu_file_quit)

        # Settings menu
        self.menu_settings = wx.Menu()
        self.test_mode_enabled = False
        self.menu_settings_testmode = self.menu_settings.AppendCheckItem(wx.ID_ANY, 'Test Mode', 'Enable/Disable Test Mode')
        self.menu_settings_setaddy = self.menu_settings.Append(wx.ID_ANY, 'Set NT Address', 'Set the robot\'s address to access the Network Table server')
        self.menu_settings_setcb = self.menu_settings.Append(wx.ID_ANY, 'Set Control Board Type', 'Sets the type of control board you are using')

        # Settings Menu - Debug Level
        self.menu_settings_debug_lvl = wx.Menu()
        self.menu_settings_debug_lvl_fatal = self.menu_settings_debug_lvl.AppendRadioItem(wx.ID_ANY, 'Fatal')
        self.menu_settings_debug_lvl_error = self.menu_settings_debug_lvl.AppendRadioItem(wx.ID_ANY, 'Error')
        self.menu_settings_debug_lvl_warn = self.menu_settings_debug_lvl.AppendRadioItem(wx.ID_ANY, 'Warning')
        self.menu_settings_debug_lvl_info = self.menu_settings_debug_lvl.AppendRadioItem(wx.ID_ANY, 'Info')
        self.menu_settings_debug_lvl_debug = self.menu_settings_debug_lvl.AppendRadioItem(wx.ID_ANY, 'Debug')
        self.menu_settings_debug_lvl_menu = self.menu_settings.AppendSubMenu(self.menu_settings_debug_lvl, 'Debug Level', 'Sets the current logger debug level')
        check_id = next(filter(lambda x: x.GetName().upper() == self.config.get_debug_level().upper(), self.menu_settings_debug_lvl.MenuItems)).GetId()
        self.menu_settings_debug_lvl.Check(check_id, True)



        self.Bind(wx.EVT_MENU, self.OnTestModeChanged, self.menu_settings_testmode)
        self.Bind(wx.EVT_MENU, self.OnSetNtAddress, self.menu_settings_setaddy)
        self.Bind(wx.EVT_MENU, self.OnCbSet, self.menu_settings_setcb)
        self.Bind(wx.EVT_MENU, self.OnDebugLevelSet, self.menu_settings_debug_lvl_fatal)
        self.Bind(wx.EVT_MENU, self.OnDebugLevelSet, self.menu_settings_debug_lvl_error)
        self.Bind(wx.EVT_MENU, self.OnDebugLevelSet, self.menu_settings_debug_lvl_warn)
        self.Bind(wx.EVT_MENU, self.OnDebugLevelSet, self.menu_settings_debug_lvl_info)
        self.Bind(wx.EVT_MENU, self.OnDebugLevelSet, self.menu_settings_debug_lvl_debug)

        # Help menu
        self.menu_help = wx.Menu()
        self.menu_help_log = self.menu_help.Append(wx.ID_ANY, 'Show Log', 'Shows the current run log')
        self.menu_help_help = self.menu_help.Append(wx.ID_ANY, 'Help', 'Shows the documentation for the control board and application')
        self.menu_help_about = self.menu_help.Append(wx.ID_ANY, 'About', 'About this application')
        self.Bind(wx.EVT_MENU, self.OnShowLog, self.menu_help_log)
        self.Bind(wx.EVT_MENU, self.OnHelp, self.menu_help_help)
        self.Bind(wx.EVT_MENU, self.OnAbout, self.menu_help_about)

        # Create menu bar
        self.menu = wx.MenuBar()
        self.menu.Append(self.menu_file, 'File')
        self.menu.Append(self.menu_settings, 'Settings')
        self.menu.Append(self.menu_help, 'Help')

        # End menu bar configuration
        ########################################

        self.tree = HTL.HyperTreeList(parent=self,
                                      id=wx.ID_ANY,
                                      agwStyle=wx.TR_DEFAULT_STYLE |
                                               wx.TR_EDIT_LABELS |
                                               wx.TR_HIDE_ROOT,
                                      )
        self.tree.AddColumn('Name')
        self.tree.AddColumn('Status')
        self.tree.AddColumn('Test Mode')
        self.tree.AddRoot('Root')
        self.tree.SetMainColumn(0)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'Control Board Type')
        self.hal_type = wx.StaticText(self, label=self.cbhal_handler.get_cbhal_inst_name())
        self.tree.SetItemWindow(label, self.hal_type, 1)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'Control Board Status')
        self.hal_status = wx.StaticText(self, label=self.DEFAULT_STATUS)
        self.tree.SetItemWindow(label, self.hal_status, 1)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'NT Server Address')
        self.nt_address = wx.StaticText(self, label=self.DEFAULT_STATUS)
        self.tree.SetItemWindow(label, self.nt_address, 1)

        label = self.tree.AppendItem(self.tree.GetRootItem(), 'NT Status')
        self.ntal_status = wx.StaticText(self, label=self.DEFAULT_STATUS)
        self.tree.SetItemWindow(label, self.ntal_status, 1)

        # Create I/O Tree Objects
        self.io_object = {}
        self.OnCreateIoTree()

        self.Bind(wx.EVT_CLOSE, self.hide_window)

        self.tree.CalculateAndSetHeaderHeight()
        self.tree.DoHeaderLayout()
        self.tree.SetColumnWidth(0, self.tree.DoGetBestSize().GetWidth())

        self.v_sizer.Add(self.tree, 1, wx.EXPAND, 0)

        self.tree.InvalidateBestSize()
        self.v_sizer.SetMinSize(self.tree.GetBestSize())

        self.Bind(wx.EVT_CLOSE, self.hide_window)
        # self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.update_test_elements)

        self.SetMenuBar(self.menu)

        self.SetSizer(self.v_sizer)

        self.update_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnUpdateTimerEvent, self.update_timer)
        self.OnTimerStart()

        # self.OnTestModeChanged()

        self.busy_updating = False
        self.update_indicators()

        self.SetAutoLayout(True)
        self.Layout()

    def OnTimerStart(self):
        self.update_timer.Start(500)

    def OnTimerStop(self):
        self.update_timer.Stop()

    def get_io_object_list(self, object_dict, object_label):
        pass

    def create_io_object(self, object_dict, object_long_name, object_short_label_prefix, num_objects, test_class=None, test_object_setup=None):

        '''

        The IO Object has the following format:
        object_dict = {'object_long_name': {'branch': <wx.TreeListItem>
                                            'branch_dict': { 'object_short_name': {'label': <wx.StaticText>
                                                                                   'status': <wx.StaticText>
                                                                                   'test': <None>, <wx.CheckBox>, <wx.Slider>
                                                                                   }
                                                           }
                                           }
                       }



        :param object_dict: The object dictionary that holds all of the status object lists
        :param object_long_name: The long label for the status object list (aka the title of the branch)
        :param object_short_label_prefix: The short label format for the list. It will be appended with the object instance number.
        :param num_objects: The number of objects to create
        :param test_object: The test wx Object to create
        :param test_object_setup: If the test wx Object needs setup, it will pass the instance to this function pointer
        :return: None
        '''


        # Check if removal needed
        if object_long_name in object_dict:
            self.logger.debug('Deleting %s children' % object_long_name)
            self.tree.DeleteChildren(object_dict[object_long_name]['branch'])
            self.tree.Delete(object_dict[object_long_name]['branch'])
            self.logger.debug('Deleting %s from object_dict.' % object_long_name)
            object_dict.update({object_long_name: None})

        # Create new branch
        self.logger.debug('Creating tree root object: %s' % object_long_name)
        branch = self.tree.AppendItem(self.tree.GetRootItem(), object_long_name)
        branch_dict = {}

        for item_num in range(num_objects):
            object_short_name = object_short_label_prefix + ' ' + str(item_num)
            self.logger.debug('Adding %s to %s' % (object_short_name, object_long_name))
            label_object = self.tree.AppendItem(branch, object_short_name)

            status_object = wx.StaticText(self, label=self.DEFAULT_STATUS)
            self.tree.SetItemWindow(item=label_object, window=status_object, column=1)

            test_object = None
            if test_class is not None:
                test_object = test_class(self)
                if test_object_setup is not None:
                    test_object_setup(test_object)
                self.tree.SetItemWindow(item=label_object, window=test_object, column=2)

            branch_dict.update({object_short_name: {'index':  item_num,
                                                    'label':  label_object,
                                                    'status': status_object,
                                                    'test':   test_object}})

        object_group = {}
        object_group.update({'branch': branch,
                             'branch_dict': branch_dict})

        object_dict.update({object_long_name: object_group})

    def setup_pwm_slider(self, slider_obj):
        slider_obj.SetMin(0)
        slider_obj.SetMax(255)


    def OnCreateIoTree(self):

        cbhal = self.cbhal_handler.get_cbhal()
        restart = False

        if cbhal.is_cbhal_running():
            cbhal.stop()
            restart = True

        expand_at_end = {}
        for (name, branch_obj) in self.io_object.items():
            is_expanded = branch_obj['branch'].IsExpanded()
            expand_at_end.update({name: is_expanded})
            if is_expanded:
                self.tree.Collapse(branch_obj['branch'])

        self.create_io_object(object_dict=self.io_object,
                              object_long_name=self.ANALOG_LNAME,
                              object_short_label_prefix=self.ANALOG_SNAME,
                              num_objects=cbhal.ANALOG_INPUTS)
        self.create_io_object(object_dict=self.io_object,
                              object_long_name=self.SWITCH_LNAME,
                              object_short_label_prefix=self.SWITCH_SNAME,
                              num_objects=cbhal.SWITCH_INPUTS)
        self.create_io_object(object_dict=self.io_object,
                              object_long_name=self.LEDS_LNAME,
                              object_short_label_prefix=self.LEDS_SNAME,
                              num_objects=cbhal.LED_OUTPUTS,
                              test_class=wx.CheckBox)
        self.create_io_object(object_dict=self.io_object,
                              object_long_name=self.PWMS_LNAME,
                              object_short_label_prefix=self.PWMS_SNAME,
                              num_objects=cbhal.PWM_OUTPUTS,
                              test_class=wx.Slider,
                              test_object_setup=self.setup_pwm_slider)
        self.Layout()
        self.tree.Refresh(True)
        self.tree.Update()
        self.Refresh(True)

        for item in expand_at_end.keys():
            if expand_at_end[item]:
                self.tree.Expand(self.io_object[item]['branch'])

        if restart:
            cbhal.start()

    def OnShowLog(self, _=None):
        # self.log_window.Show()
        self.logger.info('Opening %s in notepad.' % LOG_PATH)
        os.system('notepad %s' % LOG_PATH)

    def OnUpdateTimerEvent(self, _=None):
        self.update_indicators()
        pass

    def OnTestModeChanged(self, _=None):
        self.test_mode_enabled = self.menu_settings_testmode.IsChecked()
        self.logger.info('Test mode switched %s' % ('on' if self.test_mode_enabled else 'off'))

        if self.test_mode_enabled:
            self.logger.info('Test mode disables NT server communication.')
            self.nt.shutdownNtClient()
        else:
            self.nt.startNtClient()

        self.update_test_elements()
        self.tree.GetColumn(2).SetShown(self.test_mode_enabled)
        self.tree.Refresh(True)
        # self.tree.Update()
        # self.Refresh(True)

    def OnDebugLevelSet(self, event):
        dbg_level = next(filter(lambda x: x.GetId() == event.GetId(), event.GetEventObject().MenuItems)).GetName().upper()
        logging.basicConfig(level=dbg_level)
        self.config.set_debug_level(dbg_level)
        self.logger.info('Debug level set to %s' % dbg_level)

    def update_test_elements(self, _=None):
        test_mode_enabled = self.isTestModeEnabled()
        self.Freeze()

        expand_at_end = {}
        # Expand all elements
        for (name, branch_obj) in self.io_object.items():
            is_expanded = branch_obj['branch'].IsExpanded()
            expand_at_end.update({name: is_expanded})
            if not is_expanded:
                self.tree.Expand(branch_obj['branch'])

        # Enable/Disable the test elements
        for branch in self.io_object.values():
            for object in branch['branch_dict'].values():
                test = object['test']
                if test:
                    test.Show(test_mode_enabled)

        # Restore the tree
        for item in expand_at_end.keys():
            if expand_at_end[item]:
                self.tree.Expand(self.io_object[item]['branch'])

        self.tree.Refresh()
        self.tree.Layout()
        self.Refresh()
        self.Update()

        self.Thaw()

    def OnSetNtAddress(self, _=None):
        cur_remote_address = self.nt.getNtServerAddress()
        ntdlg = SetAddressBox(self, cur_remote_address)
        ntdlg.ShowModal()
        if ntdlg.okPressed():
            new_remote_address = ntdlg.getAddress()
            if new_remote_address != self.config.get_nt_server_address():
                self.config.set_nt_server_address(new_remote_address)
                self.nt.setNtServerAddress(new_remote_address)
        ntdlg.Destroy()

    def OnCbSet(self, _=None):
        cbdlg = SetControlBoardBox(self, self.config.get_cb_type(), self.cbhal_handler)
        cbdlg.ShowModal()
        if cbdlg.wasOkPressed():
            if cbdlg.get_cb_type_sel() != self.config.get_cb_type():
                if cbdlg.get_cb_type_sel() in self.cbhal_handler.get_types().keys():
                    self.config.set_cb_type(cbdlg.get_cb_type_sel())
                    self.hal_type.SetLabelText(cbdlg.get_cb_type_name())
                    self.OnTimerStop()
                    self.cbhal_handler.shutdown_cbhal()
                    self.cbhal_handler.init_cbtype_inst(cbdlg.get_cb_type_sel())
                    self.nt.reset_table()
                    self.OnCreateIoTree()
                    self.cbhal_handler.start_cbhal()
                    self.OnTimerStart()
                else:
                    self.logger.error('An invalid control board type selection was made.')
                cbdlg.Destroy()


    def OnAbout(self, _=None):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self, _=None):
        self.logger.info('Help button pressed')

    def hide_window(self, _=None):
        self.logger.info('Hiding the main window')
        self.Hide()

    def show_window(self, _=None):
        if not self.IsShown():
            self.logger.info('Showing the main window')
            self.Show()
        if self.IsIconized():
            self.logger.info('Un-minimizing the main window')
            self.Iconize(False)
        self.Raise()

    def exit_app(self, _=None):
        self.logger.info('User has requested to quit the ControlBoardApp')
        self.update_timer.Stop()
        self.cbhal_handler.set_event_handler(None)
        self.cbhal_handler.shutdown_cbhal()
        self.tb_icon.Destroy()
        self.Hide()
        self.Destroy()

    def isTestModeEnabled(self):
        return self.test_mode_enabled

    def updateHalWithTestValues(self, _=None):
        if self.cbhal_handler.is_valid():
            cbhal = self.cbhal_handler.get_cbhal()
            cbhal.putLedValues([val[1] for val in sorted([(led_obj['index'], led_obj['test'].IsChecked()) for led_obj in self.io_object[self.LEDS_LNAME]['branch_dict'].values()])])
            cbhal.putPwmValues([val[1] for val in sorted([(pwm_obj['index'], pwm_obj['test'].GetValue()) for pwm_obj in self.io_object[self.PWMS_LNAME]['branch_dict'].values()])])

    def event_responder(self):
        if self.isTestModeEnabled():
            wx.CallAfter(self.updateHalWithTestValues)
        else:
            self.nt.update()
        wx.CallAfter(self.update_indicators)
        pass

    def get_hal_status(self, is_running, state, update_rate):
        if is_running:
            if update_rate is not None:
                return 'Running, Updating @ ' + str(int(update_rate)) + ' Hz'
            else:
                return 'Running, Calculating update rate...'
        else:
            return state

    def update_tree_status(self, gui_element, status):
        if gui_element.GetLabelText() != str(status):
            gui_element.SetLabelText(str(status))

    def update_indicators(self):

        if not self.busy_updating:

            self.busy_updating = True

            try:

                self.update_tree_status(self.nt_address, self.nt.getNtServerAddress())
                self.update_tree_status(self.ntal_status, self.nt.get_status())

                if self.cbhal_handler.is_valid():
                    hal_status = self.cbhal_handler.get_cbhal().get_status()
                    self.tb_icon.update_icon(ctrlb_good=hal_status['IsRunning'], nt_good=self.nt.get_status() == self.nt.STATUS_CLIENT_CONNECTED)
                    if self.IsShown():
                        # Update the statuses at the top of the window
                        self.update_tree_status(self.hal_status, self.get_hal_status(is_running=hal_status['IsRunning'],
                                                                                     state=hal_status['State'],
                                                                                     update_rate=hal_status['UpdateRate']))

                        # Update the statuses of the I/O
                        if hal_status['IsRunning']:
                            for ana_obj in self.io_object[self.ANALOG_LNAME]['branch_dict'].values():
                                self.update_tree_status(ana_obj['status'], hal_status['ANAs'][ana_obj['index']])
                            for sw_obj in self.io_object[self.SWITCH_LNAME]['branch_dict'].values():
                                self.update_tree_status(sw_obj['status'], 'Closed' if hal_status['SWs'][sw_obj['index']] else 'Open')
                            for led_obj in self.io_object[self.LEDS_LNAME]['branch_dict'].values():
                                self.update_tree_status(led_obj['status'], 'On' if hal_status['LEDs'][led_obj['index']] else 'Off')
                            for pwm_obj in self.io_object[self.PWMS_LNAME]['branch_dict'].values():
                                self.update_tree_status(pwm_obj['status'], hal_status['PWMs'][pwm_obj['index']])
                        else:
                            for ana_obj in self.io_object[self.ANALOG_LNAME]['branch_dict'].values():
                                self.update_tree_status(ana_obj['status'], self.DEFAULT_STATUS)
                            for sw_obj in self.io_object[self.SWITCH_LNAME]['branch_dict'].values():
                                self.update_tree_status(sw_obj['status'], self.DEFAULT_STATUS)
                            for led_obj in self.io_object[self.LEDS_LNAME]['branch_dict'].values():
                                self.update_tree_status(led_obj['status'], self.DEFAULT_STATUS)
                            for pwm_obj in self.io_object[self.PWMS_LNAME]['branch_dict'].values():
                                self.update_tree_status(pwm_obj['status'], self.DEFAULT_STATUS)

                            self.Update()
            except:
                pass

            self.busy_updating = False
