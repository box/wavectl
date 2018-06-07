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

    def getNewestPullBranch(self, r, pullBranchSuffix):
        """In the given repo there should be several pull branches named line
        <creation-datetime><pullBranchSuffix>. This function returns the newest one
        of those pull branches"""

        # Get all the pull branches and sort them according to their name
        def getNameOfBranch(b): return b.name
        pb = sorted([h for h in r.heads if h.name.endswith(pullBranchSuffix)],
                    key=getNameOfBranch)

        # The last element is the newest pull branch
        b = pb[-1]
        return b

    def repoDirHasUntrackedFiles(self, rsrcType, rsrcs):
        """The repoDir has some untracked files and the user attempts to do a
        pull."""

        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            self.createPullBranch(r, wavectl.PullCommand.datetimeFormat,
                                  wavectl.PullCommand.pullBranchSuffix)

            # Create a new file in the repoDir without adding it to the index
            n = "newFile"
            fn = os.path.join(d, n)
            with open(fn, "w") as f:
                f.write("Some new modification")

            # The alert pull command is expected to work even though there are some
            # uncommitted_files in the repo. So we should expect to see these files
            # in the repoDir
            self.executePull(rsrcType, d, r, rsrcs, additionalFileNames=[
                             n], pullAdditionalParams=["--inGit"])

    def test_repoDirHasUntrackedFiles(self):
        self.repoDirHasUntrackedFiles("alert", util.allAlerts)
        self.repoDirHasUntrackedFiles("dashboard", util.allDashboards)

    def noChangePull(self, rsrcType, rsrcs):
        """Between two pull attempts there has not been any change to the
        resources. The second pull should just work even though there is nothing
        to commit"""

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

            # Current time is used for the branch names. So we need to wait for
            # some time to elapse so a new pull branch with a different name
            # can be created.
            time.sleep(2)

            oldRef = r.head.ref
            oldCommit = r.head.commit

            # Without any change, do another pull
            self.executePull(
                rsrcType,
                d,
                r,
                rsrcs,
                pullAdditionalParams=["--inGit"])

            # Since there has not been any change to the resources. The head
            # and the commit should not change
            self.assertEqual(oldRef, r.head.ref)
            self.assertEqual(oldCommit, r.head.commit)

    def test_noChangePull(self):
        self.noChangePull("alert", util.allAlerts)
        self.noChangePull("dashboard", util.allDashboards)

    def noBranchNameForMergeIntoBranch(self, rsrcType, rsrcs):
        """The "noBranchName" is passed as merge-into-branch parameter. We do not
        expect any merge to the master branch to happen. The pull operation
        should only create a pull branch and switch back to the initial branch"""

        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            self.createPullBranch(r, wavectl.PullCommand.datetimeFormat,
                                  wavectl.PullCommand.pullBranchSuffix)

            # Since the --merge-into-branch parameter was passed as None, there
            # should not be any resource files in the master branch.
            self.executePull(
                rsrcType, d, r, [], pullAdditionalParams=[
                    "--inGit", "--merge-into-branch", "None"])

            # However resources should exist in the latest pull branch.
            # In case of --merge--into-branch=None, the pull still happens. But the
            # retrieved files are not merged into any other branch.
            npb = self.getNewestPullBranch(
                r, wavectl.PullCommand.pullBranchSuffix)
            npb.checkout()

            self.checkFilesInDir(
                rsrcType, rsrcs, d, additionalFileNames=["README.md"])
            self.assertTrue(not r.is_dirty(untracked_files=True))

    def test_noBranchNameForMergeIntoBranch(self):
        self.noBranchNameForMergeIntoBranch("alert", util.allAlerts)
        self.noBranchNameForMergeIntoBranch("dashboard", util.allDashboards)

    def multiPull(
            self,
            rsrcType,
            rsrcs,
            firstExpectedRsrs,
            firstAdditionalParams,
            secondExpectedRsrs,
            secondAdditionalParams):
        """Execute multiple pull operations and make sure all expected resources
        are in the final directory"""

        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            self.createPullBranch(r, wavectl.PullCommand.datetimeFormat,
                                  wavectl.PullCommand.pullBranchSuffix)

            self.executePull(rsrcType, d, r,
                             firstExpectedRsrs, pullAdditionalParams=["--inGit"],
                             rsrcAdditionalParams=firstAdditionalParams)

            time.sleep(2)

            self.executePull(rsrcType, d, r,
                             secondExpectedRsrs,
                             pullAdditionalParams=["--inGit"],
                             rsrcAdditionalParams=secondAdditionalParams)

    def test_multiPull(self):
        """Execute multiple pull operations and make sure all expected resources
        are in the final directory"""
        self.multiPull(
            "alert",
            util.allAlerts,
            [util.Alert.nameMatch],
            ["--name", util.Alert.matchString],
            [util.Alert.additionalInformationMatch, util.Alert.nameMatch],
            ["--additionalInformation", util.Alert.matchString])

        self.multiPull(
            "dashboard",
            util.allDashboards,
            [util.Dashboard.kubeBoxPki],
            ["--name", util.Dashboard.kubeBoxPkiNameMatchString],
            [util.Dashboard.kubeBoxPki, util.Dashboard.skynetMonitoring],
            ["--name", util.Dashboard.skynetMonitoringNameMatchString])

    def pullWithoutAPullBranch(self, rsrcType, rsrcs):
        """ The repo does not have a pull branch. That should mean that this is
        the first pull happening to this git repo. In that case the pull
        operation creates the pull branch from the current branch the repo was
        on."""

        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            # Do not create a pull branch !!

            self.executePull(
                rsrcType,
                d,
                r,
                rsrcs,
                pullAdditionalParams=["--inGit"])

    def test_pullWithoutAPullBranch(self):
        self.pullWithoutAPullBranch("alert", util.allAlerts)
        self.pullWithoutAPullBranch("dashboard", util.allDashboards)


if __name__ == '__main__':
    #  util.initLog()
    util.unittestMain()
