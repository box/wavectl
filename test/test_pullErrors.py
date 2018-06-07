#!/usr/bin/env python

# This file contains negative tests for the pull command.

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
import re
from wavectl.Mutator import Mutator

import util


class Test(util.TestPull):
    """ A class that checks for error conditions in the `pull` command"""

    def repoDirIsFile(self, rsrcType, rsrcs):
        """ The passed repo dir exists but it is actually a file"""
        f = tempfile.NamedTemporaryFile(mode="w")

        # Deliberately pass a file name to the repoDir parameter
        args = ["pull", f.name, "--inGit", rsrcType]

        wc = wavectl.Wavectl(
            designForTestArgv=args,
            designForTestRsrcs=rsrcs)
        self.assertRaisesRegexp(
            wavectl.Error,
            "The given path: .+ is not a dir",
            wc.runCmd)

    def test_repoDirIsFile(self):
        """ The passed repo dir exists but it is actually a file"""
        self.repoDirIsFile("alert", util.allAlerts)
        self.repoDirIsFile("dashboard", util.allDashboards)

    def test_existingRepoDirNotGit(self):
        """ The repoDir is an existing directory however it is not a source
        controlled directory. The pull <rsrcs>  command should raise an exception"""
        self.existingRepoDirNotGit("pull", "alert", util.allAlerts)
        self.existingRepoDirNotGit("pull", "dashboard", util.allDashboards)

    def test_repoIndexIsDirtyInPullDir(self):
        """In this testcase, the repo has staged changes that have not been
        committed yet in the same dir as the pull dir. The pull command should
        not allow this to happen. We expect the initial branch to be without any
        outstanding modifications"""
        self.repoIndexIsDirtyInUsedDir("pull", "alert", util.allAlerts,
                                       wavectl.PullError)
        self.repoIndexIsDirtyInUsedDir("pull", "dashboard", util.allDashboards,
                                       wavectl.PullError)

    (index, workingTree) = range(2)

    def repoIsDirtyInDifferentDir(self, rsrcType, rsrcs, whatIsDirty):
        """Execute a pull operation on a git repo that is dirty because of
        some changes in another directory than the pull directory. Depending on
        the whatIsDirty parameter the changes may be staged or not-yet-staged."""
        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            self.createPullBranch(r, wavectl.PullCommand.datetimeFormat,
                                  wavectl.PullCommand.pullBranchSuffix)

            cleanSubdirName = "cleanSubdir"
            cleanSubdir = os.path.join(d, cleanSubdirName)
            os.mkdir(cleanSubdir)

            dirtySubdirName = "dirtySubdir"
            dirtySubdir = os.path.join(d, dirtySubdirName)
            os.mkdir(dirtySubdir)

            newFileName = "file1"
            self.addNewFileToRepo(r, newFileName, subdir=dirtySubdirName)

            if whatIsDirty == self.index:
                pass
            elif whatIsDirty == self.workingTree:
                # In order to make the working tree dirty we commit the file
                # and make a local modification on it.
                r.index.commit(
                    "Initial commit of {0} file".format(newFileName))

                # File1 has local modifications in a separate subdir from the
                # actual pull directory.
                fp = os.path.join(d, dirtySubdirName, newFileName)
                with open(fp, "r+") as f:
                    f.write("Some new modification")
            else:
                assert not "Unexpected value in whatIsDirty"

            assert(r.is_dirty())

            args = ["pull", d, "--inGit", rsrcType]

            wc = wavectl.Wavectl(
                designForTestArgv=args,
                designForTestRsrcs=rsrcs)

            self.assertRaisesRegexp(
                wavectl.PullError,
                (r"The path at .+ is dirty. "
                 r"Please commit your outstanding changes .*"),
                wc.runCmd)

    def test_repoIndexIsDirtyInDifferentDir(self):
        """ Execute a pull operation to a subdir in a git repo. The git
        repo has other staged changes in other subdirs, but the
        pulled-into subdir is clean. Pull operation should complain about this
        state. Pull creates other branches and does commits. We would like to be
        conservative and return an error in this scenario"""
        self.repoIsDirtyInDifferentDir("alert",
                                       util.allAlerts,
                                       self.index)
        self.repoIsDirtyInDifferentDir("dashboard",
                                       util.allDashboards,
                                       self.index)

    def test_repoWorkingTreeIsDirtyInPullDir(self):
        """Git repo has local modifications to tracked files that have not
        been staged yet in the same dir as the pull dir. The working tree is
        dirty. The pull command should not allow a pull to execute in this
        state"""
        self.repoWorkingTreeIsDirtyInUsedDir("pull", "alert", util.allAlerts,
                                             wavectl.PullError)
        self.repoWorkingTreeIsDirtyInUsedDir(
            "pull", "dashboard", util.allDashboards, wavectl.PullError)

    def test_repoWorkingTreeIsDirtyInDifferentDir(self):
        """Execute a pull operation to a subdir in a git repo. The git
        repo has other modifications in other subdirs, but the
        pulled-into subdir is clean. Pull operation should complain about this
        state. Pull creates other branches and does commits. We would like to be
        conservative and return an error in this scenario"""
        self.repoIsDirtyInDifferentDir(
            "alert", util.allAlerts, self.workingTree)
        self.repoIsDirtyInDifferentDir("dashboard", util.allDashboards,
                                       self.workingTree)

    def mergeConflictDuringPull(self, rsrcType, rsrcs):
        """By the time we execute a pull, there has been changes both
        on the local files and on the wavefront database, so that the pull
        results in a merge conflict. The wavectl raises and exception and
        expects the user to resolve this merge conflict and merge the
        pull branch manually to the desired branch (possibly the master branch)"""

        with util.TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            self.createPullBranch(r, wavectl.PullCommand.datetimeFormat,
                                  wavectl.PullCommand.pullBranchSuffix)

            self.executePull(rsrcType, d, r, rsrcs,
                             pullAdditionalParams=["--inGit"])

            rt = util.resourceTypeFromString(rsrcType)

            # Get the first resource and modify it locally. Without changing the
            # passed rsrcs collection
            rsrc = copy.deepcopy(rsrcs[0])

            # Do the local change
            # Some key name that exists in all supported resources
            conflictingField = "name"
            oldValue = rsrc[conflictingField]
            rsrc[conflictingField] = "Adding some local change " + oldValue
            uniqueId = str(rsrc[rt._uniqueKey])
            with open(os.path.join(d, uniqueId + rt.fileExtension()), "w") as f:
                # The separators avoid the trailing whitespace.
                json.dump(
                    rsrc,
                    f,
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': '))
            r.index.add([f.name])
            r.index.commit("Modified the file: {0}".format(
                uniqueId + rt.fileExtension()))

            assert(not r.is_dirty())

            # TODO: Maybe the pull branch name should contain a microsecond portion
            # wait so that the new pull branch name would be different.
            time.sleep(2)

            # Modify the same alert in a different way "remotely"
            rsrc[conflictingField] = "Adding some remote change " + oldValue

            # The first rsrcs has been modified and duplicated in one variable
            # the rest comes from the function parameters.
            # Re-mock the rsrcTypes to return the newly modified resource
            # collection.
            util.mockRsrcType(rt, [rsrc] + rsrcs[1:], [])

            try:
                self.executePull(
                    rsrcType, d, r, rsrcs, pullAdditionalParams=["--inGit"])
            except git.GitCommandError as e:
                assert re.search(
                    (r"stdout: 'Auto-merging .+\.(alert|dashboard).*\n.*"
                     r"CONFLICT [(].+[)]: "
                     r"Merge conflict in .*\.(alert|dashboard).*\n.*"
                     r"Automatic merge failed; "
                     r"fix conflicts and then commit the result.'"),
                    e.stdout)
            else:
                assert not "Missing expected exception"

    def test_mergeConflictDuringPull(self):
        self.mergeConflictDuringPull("alert", util.allAlerts)
        self.mergeConflictDuringPull("dashboard", util.allDashboards)


if __name__ == '__main__':
    #  util.initLog()
    util.unittestMain()
