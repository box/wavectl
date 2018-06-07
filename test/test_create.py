#!/usr/bin/env python

# This file contains positive tests for create command

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
import datetime
import json
import random
import socket


from wavectl.BaseWavefrontCommand import BaseWavefrontCommand
from wavectl.Mutator import Mutator
import git

import util
import wavefront_api_client


class Test(util.TestMutate):

    def executeCreate(self, rsrcType, target):
        """Call create call on target and return the generated output"""

        args = ["create", target,
                "--wavefrontHost", util.wavefrontHostName,
                "--apiToken", util.wavefrontApiToken] \
            + [rsrcType]
        wc = wavectl.Wavectl(designForTestArgv=args)

        with util.StdoutCapture() as captOut:
            wc.runCmd()

        return captOut.str()

    def createSingleRsrc(self, rsrcType, rsrc, expectedOutRegex):
        """Test the creation of one rsrc. Write the json blob of the given rsrc
        on a file and call create on it. Create function prints out the
        summary line for the created rsrc. After create's completion,
        compare the stdout"""

        with util.TempDir() as td:
            d = td.dir()

            # Write the selected resource to create it in the wavefront
            # server via wavectl create.
            rt = util.resourceTypeFromString(rsrcType)
            targetFile = tempfile.NamedTemporaryFile(
                mode="w", dir=d, delete=False, suffix=rt.fileExtension())
            json.dump(rsrc, targetFile)
            targetFile.close()  # so that writes are flushed.

            out = self.executeCreate(rsrcType, targetFile.name)

            actualOut = out.strip().split("\n")
            util.SummaryLineProcessor.compareExpectedActualLineByLine(
                self, expectedOutRegex, actualOut)

    def test_createSingleFile(self):
        """Using only one file, create the resouces described in that file"""

        expectedOut = [r"Created alert\(s\):"]
        expectedOut.append(r"ID\s*NAME\s*STATUS\s*SEVERITY")
        rsrcToCreate = util.Alert.kubernetesSkynetTag
        expectedOut.append(
            util.SummaryLineProcessor.expectedAlertSummaryLineRegex(rsrcToCreate))
        self.createSingleRsrc("alert", rsrcToCreate, expectedOut)

        expectedOut = [r"Created dashboard\(s\):"]
        expectedOut.append(r"ID\s*NAME\s*DESCRIPTION")
        rsrcToCreate = util.Dashboard.kubeBoxPki
        expectedOut.append(
            util.SummaryLineProcessor.expectedDashboardSummaryLineRegex(rsrcToCreate))
        self.createSingleRsrc("dashboard", rsrcToCreate, expectedOut)


if __name__ == '__main__':
    util.initLog()
    util.unittestMain()
