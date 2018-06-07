#!/usr/bin/env python

# Tests for pulling into a git repo dir. The directory hosts a git repo

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

    def existingRepoDir(self, rsrcType, rsrcs):
        """The pull <rsrc> command is passed a directory that is an already
        initialized empty git repo. Command impl should use that directory
        and add files to it."""
        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            self.createPullBranch(r, wavectl.PullCommand.datetimeFormat,
                                  wavectl.PullCommand.pullBranchSuffix)

            self.executePull(rsrcType, d, r, rsrcs,
                             pullAdditionalParams=["--inGit"])

    def test_existingRepoDir(self):
        self.existingRepoDir("alert", util.allAlerts)
        self.existingRepoDir("dashboard", util.allDashboards)

    def newRepoDir(self, rsrcType, rsrcs, nested=False):
        """The pull <rsrc> command is passed a path that does not exist yet.
        The impl should create a git repo there and check in files. If nested
        is true, the pulled dir has other intermediate directories that also do
        not exist."""

        d = tempfile.mkdtemp()
        shutil.rmtree(d, ignore_errors=True)

        pulledDir = d
        if nested:
            # We want to use a nested pulledDir. Have another intermediate
            # directory that does not exist.
            pulledDir = os.path.join(d, "leafDir")

        self.executePull(rsrcType, pulledDir, None, rsrcs,
                         pullAdditionalParams=["--inGit"])

        r = git.Repo(pulledDir)

        shutil.rmtree(d, ignore_errors=True)

    def test_newRepoDir(self):
        self.newRepoDir("alert", util.allAlerts)
        self.newRepoDir("dashboard", util.allDashboards)

    def test_newNestedRepoDir(self):
        self.newRepoDir("alert", util.allAlerts, nested=True)
        self.newRepoDir("dashboard", util.allDashboards, nested=True)

    (existingDir, newDir) = range(2)

    def pullIntoSubdirInRepo(self, rsrcType, rsrcs, subdirState):
        """The given directory is to a subdir of a git repo. Depending on the
        subdirState parameter, the pull happens on an existing subdir or on a
        new subdir."""

        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            self.createPullBranch(r, wavectl.PullCommand.datetimeFormat,
                                  wavectl.PullCommand.pullBranchSuffix)

            subdirName = "subdir"
            subdir = os.path.join(d, subdirName)

            if subdirState == self.existingDir:
                os.mkdir(subdir)

            self.executePull(rsrcType, subdir, r, rsrcs,
                             pullAdditionalParams=["--inGit"])

            repoInSubdir = git.Repo(subdir, search_parent_directories=True)

            self.assertEqual(r.working_tree_dir, repoInSubdir.working_tree_dir)

    def test_pullIntoSubdirInRepo(self):
        self.pullIntoSubdirInRepo("alert",
                                  util.allAlerts,
                                  self.existingDir)
        self.pullIntoSubdirInRepo("alert",
                                  util.allAlerts,
                                  self.newDir)

        self.pullIntoSubdirInRepo("dashboard",
                                  util.allDashboards,
                                  self.existingDir)
        self.pullIntoSubdirInRepo("dashboard",
                                  util.allDashboards,
                                  self.newDir)


if __name__ == '__main__':
    #  util.initLog()
    util.unittestMain()
