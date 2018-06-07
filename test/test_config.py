#!/usr/bin/env python

# This file contains positive tests for config command

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
# Extend that path so that we can import the module under test.
sys.path.insert(0, os.path.abspath('..'))

import wavectl

import tempfile
import unittest
import shutil
try:
    # Python 2
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import json
import threading


import util


class Test(unittest.TestCase):

    def configFileCreationTest(self, d, hostNameEntry, apiTokenEntry):
        """Test basic functionality. You call config and specify the
        entries. The generated config file should contain the same information"""

        args = ["config"]
        wc = wavectl.Wavectl(designForTestArgv=args, designForTestConfigDir=d)

        input = StringIO()
        input.write(hostNameEntry)
        input.write(apiTokenEntry)

        with util.StdinRedirect(input) as redIn:
            wc.runCmd()

        # In the config dir, a config file must be created.
        self.assertListEqual([wc.config.configFileName], os.listdir(d))

        fn = os.path.join(d, wc.config.configFileName)
        with open(fn) as f:
            c = json.load(f)

        # Check the values in the read config.
        self.assertDictEqual(
            c,
            {wc.config.wavefrontHostKey: hostNameEntry.strip(),
                wc.config.apiTokenKey: apiTokenEntry.strip(),
             })

    def test_configFileCreation(self):
        """Test basic functionality. You call config and specify the
        entries. The generated config file should contain the same information.
        Make sure that the config file creation works if the configDir exists
        already or not and an old config file exists already or not """

        hostNameEntry = "TestHostName\n"
        apiTokenEntry = "TestApiKey\n"

        # Config Dir    Config File
        #  Exists         Exists
        with util.TempDir() as td:
            d = td.dir()
            with open(os.path.join(d, wavectl.ConfigCommand.configFileName), "w"):
                self.configFileCreationTest(d, hostNameEntry, apiTokenEntry)

        # Config Dir    Config File
        #  Exists         Does Not
        with util.TempDir() as td:
            d = td.dir()
            self.configFileCreationTest(d, hostNameEntry, apiTokenEntry)

        # Config Dir    Config File
        #  Does Not       Does Not
        d = tempfile.mkdtemp()
        shutil.rmtree(d, ignore_errors=True)
        self.configFileCreationTest(d, hostNameEntry, apiTokenEntry)


if __name__ == '__main__':
    util.unittestMain()
