#!/usr/bin/env python

# This file contains negative tests for the show command.

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
    """ A class that checks for error conditions in the `show` command"""

    def tooManyRsrcsToDisplayInBrowser(self, rsrcType, rsrcs, maxBrowserTabs):
        """If we have too many selected rsrcs, displaying them in a
        browser should throw an exception saying that it is not allowed.
        This function checks for that error reporting"""

        with util.EnvModifier("MAX_BROWSER_TABS", maxBrowserTabs) as em:
            args = ["show", "--in-browser", rsrcType]
            wc = wavectl.Wavectl(
                designForTestArgv=args,
                designForTestRsrcs=rsrcs)

            # In this test we should attempt to open more tabs than allowed.
            # Checking that we are actually doing that.
            assert(len(rsrcs) > wc.show._maxBrowserTabs())

            # This show call prints a lot of lines to the output. Avoid the
            # print out by capturing the output
            with util.StdoutCapture() as capturedOut:
                self.assertRaisesRegexp(
                    wavectl.ShowError,
                    "Too many resources to display in browser.*",
                    wc.runCmd)

    def test_tooManyRsrcsToDisplayInBrowser(self):
        self.tooManyRsrcsToDisplayInBrowser("alert", util.allAlerts, None)
        self.tooManyRsrcsToDisplayInBrowser("alert",
                                            [util.Alert.nameMatch,
                                             util.Alert.additionalInformationMatch,
                                             util.Alert.nameMatch],
                                            "2")

        self.tooManyRsrcsToDisplayInBrowser(
            "dashboard", util.allDashboards, None)
        self.tooManyRsrcsToDisplayInBrowser("dashboard",
                                            [util.Dashboard.kubeBoxPki,
                                             util.Dashboard.skynetApplier,
                                             util.Dashboard.skynetMonitoring],
                                            "2")

    def test_invalidMaxBrowserTabs(self):
        """The user specified an invalid value to the maxBrowserTabs env var.
        It should fall back to the default 10."""
        self.tooManyRsrcsToDisplayInBrowser(
            "alert", util.allAlerts, "invalidNumber")
        self.tooManyRsrcsToDisplayInBrowser("dashboard", util.allDashboards,
                                            "invalidNumber")


if __name__ == '__main__':
    util.unittestMain()
