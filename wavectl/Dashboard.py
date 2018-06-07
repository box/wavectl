
import json
import termcolor
import collections
import copy
import abc
from six import with_metaclass

import wavefront_api_client


from .Resource import Resource


class Meta(abc.ABCMeta):
    def __str__(self):
        return "dashboard"


class Dashboard(with_metaclass(Meta, Resource)):
    """ A class representing a Dashboard"""

    def __str__(self):
        s = self.summaryTableRow(False)
        return s

    __repr__ = __str__

    # Some fields in alerts are not interesting. Omit displaying and saving
    # them.
    _omittedFields = set([
        "viewsLastDay",
        "viewsLastMonth",
        "viewsLastWeek",
    ])

    # The command line options used to narrow down Alert resources.
    _supportedFilters = {
        "id": "i",
        "name": "n",
        "description": "d",
        "updaterId": "s",
    }

    _summaryTableKeys = ["id", "name", "description"]
    _uniqueKey = "id"
    _coloredKeys = []

    @staticmethod
    def getFunction(wavefrontClient):
        """Given a wavefrontClient object return the function to call to get all
        dashboards from the wavefront Api server"""
        api = wavefront_api_client.SearchApi(wavefrontClient)
        f = api.search_dashboard_entities
        return f

    @staticmethod
    def getDeletedFunction(wavefrontClient):
        """Given a wavefrontClient object return the function to call to get all
        deleted dashboards from the wavefront Api server"""
        api = wavefront_api_client.SearchApi(wavefrontClient)
        f = api.search_dashboard_deleted_entities
        return f

    @staticmethod
    def updateFunction(wavefrontClient):
        """Given a wavefrontClient object return the function to call to update
        one dashboard in wavefront api server"""
        api = wavefront_api_client.DashboardApi(wavefrontClient)
        f = api.update_dashboard
        return f

    @staticmethod
    def createFunction(wavefrontClient):
        """Given a wavefrontClient object return the function to call to create
        one new dashboard in wavefront api server"""
        api = wavefront_api_client.DashboardApi(wavefrontClient)
        f = api.create_dashboard
        return f

    @staticmethod
    def fileExtension():
        """Return the extension used for the file on disc representing this
        resource """
        return ".dashboard"

    def __init__(self, state):

        super(Dashboard, self).__init__(state)

        # Save a reference of self to the static global list.
        self.allRsrcs.append(self)

    @classmethod
    def fromDict(cls, dict):
        """Create a Dashboard object from the given dict dictionary"""
        return cls(dict)

    def uniqueId(self):
        return self._state[Dashboard._uniqueKey]

    def browserUrlSuffix(self):
        return "/dashboard/" + str(self.uniqueId())

    def summaryTableRow(self, enableColor):
        # Return the one line summary string. This string becomes the row in the
        # summary table representing this alert.

        fmt = self._summaryTableRowFormat(enableColor)
        row = fmt.format(
            **{k: self._state.get(k, "") for k in Dashboard._summaryTableKeys})
        return row
