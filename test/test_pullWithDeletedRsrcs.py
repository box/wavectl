#!/usr/bin/env python

# This file contains positive tests for pull command

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

    def deletedRsrcs(self, rsrcType, rsrcs):
        """Some resources get deleted in the wavefront gui. Make sure
        consecutive pulls do not retain those resources. The resource' files in
        the pull directory also get deleted in following pulls"""

        assert len(
            rsrcs) > 5 and "This test expects to have a handful of resources"

        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            self.createPullBranch(r, wavectl.PullCommand.datetimeFormat,
                                  wavectl.PullCommand.pullBranchSuffix)

            self.executePull(
                rsrcType,
                d,
                r,
                rsrcs,
                pullAdditionalParams=["--inGit"])

            time.sleep(2)

            # Mock the deleted rsrcs call to return a value.
            rt = util.resourceTypeFromString(rsrcType)
            util.mockRsrcType(rt, rsrcs[2:], rsrcs[0:2])

            # Do another pull. After that make sure that the deleted alert's file
            # also disappears.
            self.executePull(
                rsrcType,
                d,
                r,
                rsrcs[2:],
                pullAdditionalParams=["--inGit"])

    def test_deletedRsrcs(self):
        self.deletedRsrcs("alert", util.allAlerts)
        self.deletedRsrcs("dashboard", util.allDashboards)


if __name__ == '__main__':
    #  util.initLog()
    util.unittestMain()
