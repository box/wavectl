#!/usr/bin/env python

# Alert state used for tests.


from __future__ import absolute_import
from __future__ import print_function

import json

import TestRsrcs


class Alert(TestRsrcs.Rsrc):
    """ A class that encompasses some alert data used for tests """

    matchPattern = r"TODO_SOME_TEST_\d+_STRING"
    matchString = "TODO_SOME_TEST_12432345_STRING"

    @staticmethod
    def getTestAlerts():
        alerts = TestRsrcs.Rsrc.getTestRsrcs("fixtures/TestAlerts.json")

        # Cherry-pick and modify some test alerts to generate better test
        # patterns
        Alert.kubernetesSkynetTag = alerts[0]
        Alert.kubernetesTag = alerts[1]
        Alert.skynetTag = alerts[2]
        Alert.nameMatch = TestRsrcs.Rsrc.appendToKey(
            Alert.matchString,
            "name",
            alerts[4])
        Alert.additionalInformationMatch = TestRsrcs.Rsrc.appendToKey(
            Alert.matchString,
            "additionalInformation",
            alerts[7])
        return alerts
