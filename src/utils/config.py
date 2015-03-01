#!/usr/bin/env python
# coding=utf-8
"""
Module to handle the configuration.
"""
__author__ = "Alkisum"

import os
import ConfigParser


class Config(object):
    """Class which handles the configuration file."""

    def __init__(self):
        """Config Constructor."""
        self.config = ConfigParser.ConfigParser()
        config_dir_name = ".pyKisum"
        config_file_name = "config"
        config_dir_path = os.path.join(os.path.expanduser("~"), config_dir_name)
        self.config_file_path = os.path.join(config_dir_path, config_file_name)
        if not os.path.isdir(config_dir_path):
            os.mkdir(config_dir_path)
        if not os.path.isfile(self.config_file_path):
            self.init_config_file()

    def init_config_file(self):
        """Write the structure of the configuration file."""
        configfile = open(self.config_file_path, 'w')
        self.config.add_section('session')
        self.config.set('session', 'library', '')
        self.config.set('session', 'playlist', '')
        self.config.write(configfile)
        configfile.close()

    def get_config_file(self):
        """Return the configuration file."""
        return self.config_file_path
