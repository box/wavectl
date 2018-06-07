#!/usr/bin/env python

# Tests for pulling into a vanilla dir. A plain directory not in git.

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
# Extend that path so that we can import the module under test.
sys.path.insert(0, os.path.abspath('..'))

import wavectl

import unittest
import shutil
import datetime
import tempfile
import time
import copy
import logging


import git

import util

import wavefront_api_client


class Test(util.TestPull):

    def existingVanillaDir(self, rsrcType, rsrcs):
        """The pull operation is done on a regular dir outside of source control"""
        with util.TempDir() as td:
            d = td.dir()
            self.executePull(rsrcType, d, None, rsrcs)

    def test_existingVanillaDir(self):
        self.existingVanillaDir("alert", util.allAlerts)
        self.existingVanillaDir("dashboard", util.allDashboards)

    def newVanillaDir(self, rsrcType, rsrcs, nested=False):
        """The pull operation is passed a path that does not exist yet and
        no git source control is used. If nested is true, the pulled dir has other
        intermediate directories that also do not exist."""

        d = tempfile.mkdtemp()
        shutil.rmtree(d, ignore_errors=True)

        pulledDir = d
        if nested:
            # We want to use a nested pulledDir. Have another intermediate
            # directory that does not exist.
            pulledDir = os.path.join(d, "leafDir")

        self.executePull(rsrcType, pulledDir, None, rsrcs)
        shutil.rmtree(d, ignore_errors=True)

    def test_newVanillaDir(self):
        self.newVanillaDir("alert", util.allAlerts)
        self.newVanillaDir("dashboard", util.allDashboards)

    def test_newNestedVanillaDir(self):
        self.newVanillaDir("alert", util.allAlerts, nested=True)
        self.newVanillaDir("dashboard", util.allDashboards, nested=True)


if __name__ == '__main__':
    #  util.initLog()
    util.unittestMain()
