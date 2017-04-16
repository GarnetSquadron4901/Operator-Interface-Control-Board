import logging

logger = logging.getLogger(__name__)

import operator
import os
import sys
from xml.etree import ElementTree as ET

if getattr(sys, 'frozen', False):
    # Normal Mode
    from ControlBoardApp.ControlBoardApp import CONFIG_PATH
else:
    # Test Mode
    from ControlBoardApp import CONFIG_PATH

# This maps the logging level strings to the actual logging level value
dbg_level_dict = {'Fatal': logging.FATAL,
                  'Error': logging.ERROR,
                  'Warning': logging.WARNING,
                  'Info': logging.INFO,
                  'Debug': logging.DEBUG}


class ConfigFile:
    def __init__(self):
        """
        ConfigFile - Provides access to the configuration file.
        """

        self.config_file_path = os.path.join(os.path.expanduser('~'), CONFIG_PATH)
        logger.info('Loading config: %s' % self.config_file_path)

        if os.path.exists(self.config_file_path):
            self.config_tree = ET.parse(self.config_file_path)
        else:
            logger.info('Config file does not exist yet. Creating a default config file.')
            self.config_tree = self.create_default_config()
            self.save_config()

        self.config_root = self.config_tree.getroot()

    def save_config(self):
        """
        Writes the live config to the config file.
        
        :return: 
        """
        logger.info('Config file saved.')
        self.config_tree.write(self.config_file_path)

    @staticmethod
    def create_default_config():
        """
        Creates a default config in cases where a config did not exist at startup. 
        
        :return: 
        """
        cb_app_config_root = ET.Element('ControlBoardAppConfig')
        cb_type = ET.SubElement(cb_app_config_root, 'ControlBoardConfig')
        cb_nt_config = ET.SubElement(cb_app_config_root, 'NetworkTableConfig')
        cb_logging = ET.SubElement(cb_app_config_root, 'LoggingConfig')
        cb_type.attrib.update({'Type': 'ControlBoard_1v1_Simulator'})
        cb_nt_config.attrib.update({'Server': 'localhost'})
        cb_logging.attrib.update({'Level': 'Warning'})
        cb_app_config_tree = ET.ElementTree(cb_app_config_root)
        return cb_app_config_tree

    def get_nt_server_address(self):
        """
        Returns the saved NT server address. 
        
        :return: str - NT server address
        """
        nt_address = self._get_attribute_from_element_path('NetworkTableConfig', 'Server', '')
        logger.info('Loaded NT server address from config: %s' % nt_address)
        return nt_address

    def set_nt_server_address(self, nt_address):
        """
        Sets the NT server address to the config file.
        :param nt_address: str - NT server address
        :return: 
        """
        logger.info('Saving NT server address to config: %s' % nt_address)
        self._set_attribute_from_element_path('NetworkTableConfig', 'Server', nt_address)
        self.save_config()

    def get_cb_type(self):
        """
        Returns the saved control board type.
        
        :return: str - control board CB_SNAME 
        """
        cb_type = self._get_attribute_from_element_path('ControlBoardConfig', 'Type', '')
        logger.info('Loaded control board type from config: %s' % cb_type)
        return cb_type

    def set_cb_type(self, cb_type):
        """
        Sets the control board type CB_SNAME to the config file.
        
        :param cb_type: str - the CB_SNAME 
        :return: 
        """
        logger.info('Saving control board type to config: %s' % cb_type)
        self._set_attribute_from_element_path('ControlBoardConfig', 'Type', cb_type)
        self.save_config()

    @staticmethod
    def get_logging_levels():
        """
        Returns all valid logging levels.
        
        :return: list - valid logging levels in order from least severe to most severe
        """
        return [level[0] for level in sorted(dbg_level_dict.items(), key=operator.itemgetter(1))]

    def get_logging_level(self):
        """
        Returns the saved logging level.
        :return: int - the logging level
        """
        return dbg_level_dict[self.get_logging_level_str()]

    def get_logging_level_str(self):
        """
        Returns teh saved logging level string.
        
        :return: str - the logging level 
        """
        level = self._get_attribute_from_element_path('LoggingConfig', 'Level', 'Warning')
        logger.info('Loaded logging level from config: %s' % level)
        return level

    def set_logging_level(self, level):
        """
        Sets the logging level to the config file.
        :param level: str - logging level
        :return: 
        """
        if level not in dbg_level_dict.keys():
            raise IndexError('Provided log level not valid.')
        logger.info('Saving logging level to config: %s' % level)
        self._set_attribute_from_element_path('LoggingConfig', 'Level', level)
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
