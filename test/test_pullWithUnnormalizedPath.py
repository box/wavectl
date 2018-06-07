#!/usr/bin/env python

# Test that the pull command can handle path parameters if the path is not
# normalized. Has characters like ../ ./ // ,etc

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

    def unnormalizedPath(self, rsrcType, rsrcs):
        """The passed directory path to the pull command may be
        unnormalized. The pull command should work regardless. For example the
        path may contain elements like /..//./"""

        dir = tempfile.mkdtemp()

        dirs = [
            dir,
            os.path.join(dir, ""),
            dir.replace("/", "//"),
            dir.replace("/", "//").replace("//", "/./"),
            os.path.join(dir, "SomeDir", ".."),
        ]

        for d in dirs:
            # Always start from a clean state. Remove the dir.
            shutil.rmtree(dir, ignore_errors=True)
            shutil.rmtree(d, ignore_errors=True)

            self.executePull(rsrcType, d, None, rsrcs,
                             pullAdditionalParams=["--inGit"])

            r = git.Repo(d)

            shutil.rmtree(d, ignore_errors=True)

    def test_unnormalizedPath(self):
        self.unnormalizedPath("alert", util.allAlerts)
        self.unnormalizedPath("dashboard", util.allDashboards)


if __name__ == '__main__':
    #  util.initLog()
    util.unittestMain()
