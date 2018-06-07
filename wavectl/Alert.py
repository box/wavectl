
import json
import termcolor
import collections
import copy
import abc
from six import with_metaclass

import wavefront_api_client


from .Resource import Resource

# To print a human readable string for the class type name


class Meta(abc.ABCMeta):
    def __str__(self):
        return "alert"


class Alert(with_metaclass(Meta, Resource)):
    """ A class representing an Alert"""

    def __str__(self):
        s = self.summaryTableRow(False)
        return s

    __repr__ = __str__

    # Some fields in alerts are not interesting. Omit displaying and saving
    # them.
    _omittedFields = set([
        "activeMaintenanceWindows",
        "alertsLastDay",
        "alertsLastMonth",
        "alertsLastWeek",
        "conditionQBEnabled",
        "created",
        "createdEpochMillis",
        "createUserId",
        "creatorId",
        "deleted",
        "displayExpressionQBEnabled",
        "endTime",
        "event",
        "failingHostLabelPairs",
        "hostsUsed",
        "inMaintenanceHostLabelPairs",
        "inTrash",
        "lastEventTime",
        "lastNotificationMillis",
        "lastProcessedMillis",
        "metricsUsed",
        "notificants",
        "pointsScannedAtLastQuery",
        "prefiringHostLabelPairs",
        "processRateMinutes",
        "queryFailing",
        "runningState",
        "runninState",
        "sortAttr",
        "startTime",
        "status",
        "targetInfo",
        "updated",
        "updatedEpochMillis",
        "updaterId",
        "updateUserId",
    ])

    # The command line options used to narrow down Alert resources.
    _supportedFilters = {
        "id": "i",
        "name": "n",
        "condition": "d",
        "displayExpression": "x",
        "additionalInformation": "f",
        "status": "a",
        "severity": "e",
    }

    # TODO : Should we add SNOOZED Until ?
    # This will make it more similar to the wavefront web page.
    _summaryTableKeys = ["id", "name", "status", "severity"]

    _uniqueKey = "id"

    @staticmethod
    def _colorStatus(v):
        """ The value is for the status field in alert data. Return its
        tty colored string accordingly"""

        if v == "CHECKING":
            return termcolor.colored(v, color="green")
        elif v == "ACTIVE" or v == "FIRING":
            return termcolor.colored(v, color="red")
        elif v == "SNOOZED":
            return termcolor.colored(v, color="grey")
        else:
            return v

    @staticmethod
    def _colorSeverity(v):
        """ The value is for the severity a field in alert data. Return its
        tty colored string accordingly"""
        if v == "SEVERE":
            return termcolor.colored(v, color="red")
        elif v == "WARN":
            return termcolor.colored(v, color="yellow")
        elif v == "INFO":
            return termcolor.colored(v, color="blue")
        elif v == "SMOKE":
            return termcolor.colored(v, color="grey")
        else:
            return v

    _coloredKeys = ["status", "severity"]

    @staticmethod
    def _maybeColor(k, v, enableColor):
        """ Depending on the key and the color setting from the command line
        we may want to color the output. This function returns the colored version
        of v if desired or if possible"""

        if not enableColor:
            return v

        # We only color-code alert states and severity information. Nothing else.
        # This is similar to the wavefront webpage interface.
        if k == "status":
            return Alert._colorStatus(v)
        elif k == "severity":
            return Alert._colorSeverity(v)
        else:
            return v

    @staticmethod
    def _formatValueForSummaryTable(k, v, enableColor):
        """Format the given value for a nice print in the summary table  """
        if isinstance(v, collections.MutableSequence):
            return " ".join([Alert._maybeColor(k, x, enableColor) for x in v])
        else:
            return Alert._maybeColor(k, v, enableColor)

    @staticmethod
    def getFunction(wavefrontClient):
        """Given a wavefrontClient object return the function to call to get all
        alerts from the wavefront Api server"""
        api = wavefront_api_client.SearchApi(wavefrontClient)
        f = api.search_alert_entities
        return f

    @staticmethod
    def getDeletedFunction(wavefrontClient):
        """Given a wavefrontClient object return the function to call to get all
        deleted alerts from the wavefront Api server"""
        api = wavefront_api_client.SearchApi(wavefrontClient)
        f = api.search_alert_deleted_entities
        return f

    @staticmethod
    def updateFunction(wavefrontClient):
        """Given a wavefrontClient object return the function to call to update
        one alert in wavefront api server"""
        api = wavefront_api_client.AlertApi(wavefrontClient)
        f = api.update_alert
        return f

    @staticmethod
    def createFunction(wavefrontClient):
        """Given a wavefrontClient object return the function to call to create
        one new alert in wavefront api server"""
        api = wavefront_api_client.AlertApi(wavefrontClient)
        f = api.create_alert
        return f

    @staticmethod
    def fileExtension():
        """Return the extension used for the file on disc representing this
        resource"""
        return ".alert"

    def __init__(self, state):
        super(Alert, self).__init__(state)

        # Save a reference of self to the static global list.
        self.allRsrcs.append(self)

    @classmethod
    def fromDict(cls, dict):
        """Create a Dashboard object from the given dict dictionary"""
        return cls(dict)

    def uniqueId(self):
        """Return a unique id representing this Alert.
        It is the id field assigned by the wavefront api server"""
        return self._state[Alert._uniqueKey]

    def browserUrlSuffix(self):
        return "/alert/" + str(self.uniqueId())

    def summaryTableRow(self, enableColor):
        # Return the one line summary string. This string becomes the row in the
        # summary table representing this alert.

        fmt = self._summaryTableRowFormat(enableColor)
        row = fmt.format(
            **{k: Alert._formatValueForSummaryTable(k, self._state.get(k, ""),
                                                    enableColor) for k in Alert._summaryTableKeys})
        return row
