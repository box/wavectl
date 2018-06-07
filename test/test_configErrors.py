#!/usr/bin/env python

# This file contains negative tests for the config command

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
# Extend that path so that we can import the module under test.
sys.path.insert(0, os.path.abspath('..'))

# Design under test.
import wavectl

import unittest
import tempfile
import git
import shutil

import util


class Test(unittest.TestCase):
    """ A class that checks for error conditions with the config files """

    def test_wavefrontHostNotFound(self):
        """In this test the user attempts to execute a command that
        reaches out to the wavefront api server. However the config file
        mentioning the host name and the api token have not been initialized yet.
        The user also has not passed command line options specifying the wavefront
        host or the api token.  There should be a raised exception"""

        # The config file dir gets deleted. So the command cannot find the
        # desired config file
        d = tempfile.mkdtemp()
        shutil.rmtree(d, ignore_errors=True)

        args = ["show", "alert"]
        # Since the designForTestRsrcs is not given, the command will try to
        # reach out to wavefront. It will """
        wc = wavectl.Wavectl(
            designForTestArgv=args,
            designForTestConfigDir=d)

        self.assertRaisesRegexp(
            wavectl.ConfigError,
            ("The wavefront host url is not known. Either execute "
             "`wavectl config ...` or pass {0} command line option").format(
                wc.pull.wavefrontHostOptionName),
            wc.runCmd)

    def test_apiTokenNotFound(self):
        """the api token is not specified. The config file is not populated and
        the command line ars do not have the --apiToken parameter. We expect
        an exception raised."""

        # The config file dir gets deleted. So the command cannot find the
        # desired config file
        d = tempfile.mkdtemp()
        shutil.rmtree(d, ignore_errors=True)

        args = ["show", "--wavefrontHost", "https://someHost.com", "alert"]
        # Since the designForTestRsrcs is not given, the command will try to
        # reach out to wavefront. It will look for the config file.
        wc = wavectl.Wavectl(
            designForTestArgv=args,
            designForTestConfigDir=d)

        self.assertRaisesRegexp(
            wavectl.ConfigError,
            ("The wavefront api token is not known. Either execute "
                "`wavectl config ...` or pass {0} command line option").format(
                wc.pull.apiTokenOptionName),
            wc.runCmd)


if __name__ == '__main__':
    util.unittestMain()
