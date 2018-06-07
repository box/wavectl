#!/usr/bin/env python

# A simple script that executes push and prints the output to std out .  This
# script is called during documentation generation time.

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
fileDir = os.path.dirname(os.path.abspath(__file__))
rootDir = os.path.realpath(os.path.join(fileDir, "..", ".."))
testDir = os.path.join(rootDir, "test")
sys.path.insert(0, rootDir)
sys.path.insert(0, testDir)
os.chdir(testDir)

import argparse
import wavectl
import test.util
import test.TestAlerts

from argparse import Namespace


def main():

    testDashboards = test.util.TestDashboards.Dashboard.getTestDashboards()[:]
    test.util.mockRsrcType(
        wavectl.Dashboard.Dashboard,
        [testDashboards[7]], [])

    with test.util.TempDir() as td:
        d = td.dir()

        ns = Namespace(
            rsrcType="dashboard",
            dir=d,
            inGit=False,
            customerTag=None,
            wavefrontHost=test.util.wavefrontHostName,
            apiToken=test.util.wavefrontApiToken)

        pl = wavectl.PullCommand()
        pl.handleCmd(ns)

        ns = Namespace(
            rsrcType="dashboard",
            target=os.path.join(d,
                                testDashboards[7][wavectl.Dashboard.Dashboard._uniqueKey])
            + wavectl.Dashboard.Dashboard.fileExtension(),
            inGit=False,
            customerTag=None,
            quiet=False,
            wavefrontHost=test.util.wavefrontHostName,
            apiToken=test.util.wavefrontApiToken)

        pu = wavectl.PushCommand()
        pu.handleCmd(ns)


if __name__ == "__main__":
    main()
