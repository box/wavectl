#!/usr/bin/env python

# Alert state used for tests.


from __future__ import absolute_import
from __future__ import print_function

import json
import TestRsrcs


class Dashboard(TestRsrcs.Rsrc):
    """ A class that encompasses some dashboard data used for tests """

    kubeBoxPkiNameMatchString = "SomeNameToBeMachedInKubeBoxPki"
    skynetMonitoringNameMatchString = "SomeMatchString"

    @staticmethod
    def getTestDashboards():
        dashboards = TestRsrcs.Rsrc.getTestRsrcs(
            "fixtures/TestDashboards.json")
        Dashboard.kubeBoxPki = TestRsrcs.Rsrc.appendToKey(
            Dashboard.kubeBoxPkiNameMatchString,
            "name",
            dashboards[0])
        Dashboard.skynetMonitoring = TestRsrcs.Rsrc.appendToKey(
            Dashboard.skynetMonitoringNameMatchString,
            "name",
            dashboards[1])
        Dashboard.skynetApplier = dashboards[2]
        return dashboards
