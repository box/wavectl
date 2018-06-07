#!/usr/bin/env python

# In this file we have positive tests of the `show ... ` cmd

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
# Extend that path so that we can import the module under test.
sys.path.insert(0, os.path.abspath('..'))

import wavectl
import unittest
import json
import copy
import re
import time
import six
import logging

import util


class Test(util.Test):

    def addCommasToDistionaryList(self, s):
        """ The string may be a back to back printed distionaries.For example:
        {a:b} {c:d} {e:f}. Python wants to have commas between the entries in a list.
        So in this function we add commas into the input string between
        disctionary entries {a:b}, {c:d}, {e:f}"""
        return re.sub(r"}\s*{", r"},\n{", s)

    def purgeOmittedFields(self, rsrcType, rsrcs):
        """A resource representation has some un-interesting fields.
        They are listed in the self.omittedFileds attribute. This function purges
        those key value pairs from each resource state. Operates on the given rsrcs
        parameter"""
        myRsrcs = copy.deepcopy(rsrcs)
        [[a.pop(k, None) for k in util.resourceTypeFromString(
            rsrcType)._omittedFields] for a in myRsrcs]
        return myRsrcs

    def executeShow(self,
                    rsrcType,
                    showAdditionalParams=[],
                    rsrcAdditionalParams=[]):
        """Execute a resource show command and return the printed std out."""

        args = ["show",
                "--wavefrontHost", util.wavefrontHostName,
                "--apiToken", util.wavefrontApiToken] \
            + showAdditionalParams \
            + [rsrcType] \
            + rsrcAdditionalParams
        wc = wavectl.Wavectl(designForTestArgv=args)

        with util.StdoutCapture() as captOut:
            wc.runCmd()

        return captOut.str()

    def fullRsrcsWithMatch(self, rsrcType, rsrcs):
        """ A basic test case for show it expects to print all data in all of the
        resources."""

        out = self.executeShow(rsrcType,
                               showAdditionalParams=["--output=json"])

        receivedRsrcs = json.loads(
            "[" + self.addCommasToDistionaryList(out) + "]")

        self.assertEqual(len(receivedRsrcs), len(rsrcs))

        # Pick some key name that exists in all rsrcTypes
        def getCommonKey(x): return x.get("name")
        actRsrcs = sorted(
            self.purgeOmittedFields(
                rsrcType,
                rsrcs),
            key=getCommonKey)
        receivedRsrcs = sorted(receivedRsrcs, key=getCommonKey)
        # TODO: Here we only compare a small subset of keys of resources. This
        # made sense when the wavectl implementation was using wavefront v1 api
        # and tests were using v2 api. Recently all code has migrated to v2 api.
        # Ideally we should be comparing a lot more keys in resources.
        compareKeys = self.getCompareKeys(rsrcType)
        self.assertTrue(all([self.compareRsrcs(r1, r2, compareKeys)
                             for (r1, r2) in zip(actRsrcs, receivedRsrcs)]))

    def test_fullRsrcsWithMatch(self):
        self.fullRsrcsWithMatch("alert", util.allAlerts)
        self.fullRsrcsWithMatch("dashboard", util.allDashboards)

    def fullRsrcsNoMatch(self, rsrcType, rsrcs):
        """ `show <rsrcType>` attempts to print the full state of resources but
        there are no matching resources"""

        out = self.executeShow(
            rsrcType,
            showAdditionalParams=["--output=json"],
            rsrcAdditionalParams=[
                "--match",
                "unlikely_string_that_does_not_match_34kjh234"])

        self.assertEqual(out.strip(), "")

    def test_fullRsrcsNoMatch(self):
        self.fullRsrcsNoMatch("alert", util.allAlerts)
        self.fullRsrcsNoMatch("dashboard", util.allDashboards)

    def summaryRsrcs(
            self,
            rsrcType,
            rsrcs,
            expectedOutRegex,
            rsrcAdditionalParams=[]):
        """ Only print the resource summaries.

        Gets the output lines from the stdout of the command.
        Compare it line by line with the given expectedOutRegex list. One regex
        per line"""

        out = self.executeShow(rsrcType,
                               rsrcAdditionalParams=rsrcAdditionalParams)

        actualOut = out.strip().split("\n")
        util.SummaryLineProcessor.compareExpectedActualLineByLine(
            self, expectedOutRegex, actualOut)

    def test_summaryRsrcsWithMatch(self):
        expectedOut = [r"ID\s*NAME\s*STATUS\s*SEVERITY"]
        for r in util.allAlerts:
            expectedOut.append(
                util.SummaryLineProcessor.expectedAlertSummaryLineRegex(r))
        self.summaryRsrcs("alert", util.allAlerts, expectedOut)

        expectedOut = [r"ID\s*NAME\s*DESCRIPTION"]
        for r in util.allDashboards:
            expectedOut.append(
                util.SummaryLineProcessor.expectedDashboardSummaryLineRegex(r))
        self.summaryRsrcs("dashboard", util.allDashboards, expectedOut)

    def test_summaryRsrcsNoMatch(self):
        """ Attempt to print resource summaries but no reseource matches the given
        regexes"""
        expectedOut = [r"ID\s*NAME\s*STATUS\s*SEVERITY"]
        self.summaryRsrcs("alert", util.allAlerts, expectedOut, rsrcAdditionalParams=[
                          "--match", "unlikely_string_that_does_not_match_34kjh234"])

        expectedOut = [r"ID\s*NAME\s*DESCRIPTION"]
        # The summary should print the created and the name for now.
        self.summaryRsrcs(
            "dashboard",
            util.allDashboards,
            expectedOut,
            rsrcAdditionalParams=[
                "--match",
                "unlikely_string_that_does_not_match_34kjh234"])

    def summaryRsrcsNoHeader(self, rsrcType):
        """Test the --no-header parameter. If --no--header is specified the
        summary table will not print an header"""

        out = self.executeShow(
            rsrcType,
            showAdditionalParams=["--no-header"],
            rsrcAdditionalParams=[
                "--match",
                "unlikely_string_that_does_not_match_34kjh234"])

        # With --no-header the output of an empty match should only me an empty
        # string
        self.assertEqual(out.strip(), "")

    def test_summaryRsrcsNoHeader(self):
        """Test the --no-header parameter. If --no--header is specified the
        summary table will not print an header"""
        self.summaryRsrcsNoHeader("alert")
        self.summaryRsrcsNoHeader("dashboard")

    def test_showWithCustomerTag(self):
        """The user passed two customerTags. In this test we first write all
        resources to the wavefront server. Then do a show with two customerTags.
        Only resources that container BOTH tags are expected to show"""
        expectedOut = [r"ID\s*NAME\s*STATUS\s*SEVERITY"]
        allAlerts = util.allAlerts
        # Only this alert has both tags.
        expectedAlerts = [util.Alert.kubernetesSkynetTag]
        for r in expectedAlerts:
            expectedOut.append(
                util.SummaryLineProcessor.expectedAlertSummaryLineRegex(r))
        self.summaryRsrcs("alert",
                          allAlerts,
                          expectedOut,
                          rsrcAdditionalParams=[
                              "--customerTag", "kubernetes",
                              "--customerTag", "skynet"])

        expectedOut = [r"ID\s*NAME\s*DESCRIPTION"]
        allDashboards = util.allDashboards
        # Only this dashboard has both tags.
        expectedDashboards = [util.Dashboard.skynetApplier]
        for r in expectedDashboards:
            expectedOut.append(
                util.SummaryLineProcessor.expectedDashboardSummaryLineRegex(r))
        self.summaryRsrcs("dashboard",
                          allDashboards,
                          expectedOut,
                          rsrcAdditionalParams=[
                              "--customerTag", "kubernetes",
                              "--customerTag", "skynet"])

# TODO:
# 1) Add a show in browser test with probably some mocking.
#


if __name__ == '__main__':
    #  util.initLog()
    util.unittestMain()
