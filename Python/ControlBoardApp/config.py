import logging
logger = logging.getLogger(__name__)

import os
from xml.etree import ElementTree as ET


class ConfigFile:
    CONFIG_FILE = 'ControlBoardConfig.xml'
    def __init__(self, filename):
        # wx.LogVerbose('Loading config: %s' % filename)
        self.config_file_path = os.path.join(os.path.expanduser('~'), self.CONFIG_FILE)

        if os.path.exists(self.config_file_path):
            self.config_tree = ET.parse(self.config_file_path)
        else:
            self.config_tree = self.create_default_config()
            self.save_config()

        self.config_root = self.config_tree.getroot()

    def save_config(self):
        self.config_tree.write(self.config_file_path)

    def create_default_config(self):
        cb_app_config_root = ET.Element('ControlBoardAppConfig')
        cb_type = ET.SubElement(cb_app_config_root, 'ControlBoardConfig')
        cb_nt_config = ET.SubElement(cb_app_config_root, 'NetworkTableConfig')
        cb_debug = ET.SubElement(cb_app_config_root, 'DebugConfig')
        cb_type.attrib.update({'Type': 'None'})
        cb_nt_config.attrib.update({'Server': 'None'})
        cb_debug.attrib.update({'Level': 'Warning'})
        cb_app_config_tree = ET.ElementTree(cb_app_config_root)
        return cb_app_config_tree

    def get_nt_server_address(self):
        return self._get_attribute_from_element_path('NetworkTableConfig', 'Server', 'None')

    def set_nt_server_address(self, nt_address):
        # wx.LogVerbose('Saving NT server address to config: %s' % nt_address)
        self._set_attribute_from_element_path('NetworkTableConfig', 'Server', nt_address)
        self.save_config()

    def get_cb_type(self):
        return self._get_attribute_from_element_path('ControlBoardConfig', 'Type', 'None')
        # wx.LogVerbose('Loaded control board type from config: %s' % cb_type)

    def set_cb_type(self, cb_type):
        # wx.LogVerbose('Saving control board type to config: %s' % cb_type)
        self._set_attribute_from_element_path('ControlBoardConfig', 'Type', cb_type)
        self.save_config()

    def get_debug_level(self):
        return self._get_attribute_from_element_path('DebugConfig', 'Level', 'Warning')

    def set_debug_level(self, level):
        self._set_attribute_from_element_path('DebugConfig', 'Level', level)
        self.save_config()



    ###########################################################################
    ##                         Private Functions                             ##
    ###########################################################################

    def _get_attribute_from_element_path(self, path, attribute, default=None):
        """ Returns the value of an given attribute name from the given element path.

        Args:
         :param path - The element tree's path
         :param attribute - The name of the attribute
         :param default - If the attribute is not found, what it will return instead, rather than raising a KeyError
         :return: value - The attribute value string
        """

        return self._get_attribute(self._get_element_from_path(path,
                                   pass_on_error=(default is not None)),
                                   attribute,
                                   default=default)

    def _set_attribute_from_element_path(self, path, attribute, value):
        """ Sets an the attribute to the value specified in the path provided.

        :param path - The path to the attribute
        :param attribute - The name of the attribute
        :param value - The value to set the attribute to
        :return:
        """

        element = self._get_element_from_path(path)
        element.attrib.update({attribute: value})

    def _get_element_from_path(self, path, pass_on_error=False):
        """ Returns the element from the provided path.

        :param path - The element's path.
        :return: element - The element
        """

        element = self.config_root.find(path)
        if element is None and not pass_on_error:
            raise KeyError('The path \"%s\" does not exist in \"%s\".' % (path, self.config_file_path))

        return element

    @staticmethod
    def _get_attribute(element, attribute, default=None):
        """ Returns the value of the given attribute form the Element Tree item.

        :param element - The Element Tree item to get the attribute value from
        :param attribute - The name of the attribute
        :param default - If the attribute is not found, what it will return instead, rather than raising a KeyError
        :return: value - The attribute value string
        """

        if element is not None:
            if attribute in element.attrib:
                return element.attrib[attribute]
            else:
                if isinstance(default, str):
                    return default
                else:
                    raise KeyError('"' + attribute + '" is not in the ' + element.tag + ' attributes.')
        else:
            if default is not None:
                return default
            else:
                raise ValueError('XML element is not valid.')
