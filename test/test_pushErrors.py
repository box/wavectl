#!/usr/bin/env python

# This file contains negative tests for the push command.

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
import copy
import json
import time

import util


class Test(util.TestPullMutate):
    """ A class that checks for error conditions in the `push` command"""

    def pushTargetDoesNotExist(self, rsrcType):
        """The push command is passed a target that does not exist.
        We expect an exception from the wavectl command"""

        nonExistingTarget = "someRandomPathDoesNotExist_lkjshfglkjdsfh"
        args = ["push", nonExistingTarget, "--inGit", rsrcType, ]
        wc = wavectl.Wavectl(designForTestArgv=args)

        self.assertRaisesRegexp(
            wavectl.Mutator.MutatorError,
            "The given path: .*" + nonExistingTarget + " does not exist",
            wc.runCmd)

    def test_pushTargetDoesNotExist(self):
        self.pushTargetDoesNotExist("alert")
        self.pushTargetDoesNotExist("dashboard")

    def pushTargetFileIsDirty(self, rsrcType):
        """Push is using one file to push. In a repo the pushed single file is
        dirty. Push should complain"""
        rt = util.resourceTypeFromString(rsrcType)

        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            fileName = "newRsrc" + rt.fileExtension()
            self.addNewFileToRepo(r, fileName)

            args = ["push", os.path.join(d, fileName), "--inGit", rsrcType]

            wc = wavectl.Wavectl(designForTestArgv=args)

            self.assertRaisesRegexp(
                wavectl.MutatorError,
                (r"The path at .+ is dirty. "
                 r"Please commit your outstanding changes .*"),
                wc.runCmd)

    def test_pushTargetFileIsDirty(self):
        self.pushTargetFileIsDirty("alert")
        self.pushTargetFileIsDirty("dashboard")

    def test_existingRepoDirNotGit(self):
        """ The repoDir is an existing directory however it is not a source
        controlled directory. The alert pull command should raise an exception"""
        self.existingRepoDirNotGit("push", "alert", util.allAlerts)
        self.existingRepoDirNotGit("push", "dashboard", util.allDashboards)

    def test_repoIndexIsDirtyInPushDir(self):
        """ Attempt to do a push while the given dir has staged but uncommitted
        changes"""
        self.repoIndexIsDirtyInUsedDir("push", "alert", util.allAlerts,
                                       wavectl.MutatorError)
        self.repoIndexIsDirtyInUsedDir("push", "dashboard", util.allDashboards,
                                       wavectl.MutatorError)

    def test_repoWorkingTreeIsDirtyInPushDir(self):
        """ Attempt to do a push from a dir that has local modifications.
        The push command should not allow for a push with local changes"""

        self.repoWorkingTreeIsDirtyInUsedDir("push", "alert", util.allAlerts,
                                             wavectl.MutatorError)
        self.repoWorkingTreeIsDirtyInUsedDir(
            "push", "dashboard", util.allDashboards, wavectl.MutatorError)


if __name__ == '__main__':
    util.unittestMain()


# Test Plan
# 1) Given push needs to be renamed to replace.
# Try to update a non-existent resource. The user should use create instead.
