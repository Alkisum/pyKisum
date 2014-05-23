#!/usr/bin/env python

import os
import ConfigParser


class Config():
    """Class which handles the configuration file."""

    def __init__(self):
        """Config Constructor."""
        self.config = ConfigParser.ConfigParser()
        configdirname = ".pyKisum"
        configfilename = "config"
        configdirpath = os.path.join(os.path.expanduser("~"), configdirname)
        self.configfilepath = os.path.join(configdirpath, configfilename)
        if not os.path.isdir(configdirpath):
            os.mkdir(configdirpath)
        if not os.path.isfile(self.configfilepath):
            self.init_config_file()

    def init_config_file(self):
        """Write the structure of the configuration file."""
        configfile = open(self.configfilepath, 'w')
        self.config.add_section('library')
        self.config.set('library', 'path', '')
        self.config.add_section('playlist')
        self.config.set('playlist', 'lastselection', '')
        self.config.write(configfile)
        configfile.close()

    def get_config_file(self):
        """Return the configuration file."""
        return self.configfilepath
