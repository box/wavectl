
import argparse

from .Resource import Resource
from .Alert import Alert
from .Dashboard import Dashboard


class ResourceFactory(object):

    @staticmethod
    def resourceTypeFromString(s):
        """ Parse the given string and return the resource type"""
        if s == "alert":
            return Alert
        if s == "dashboard":
            return Dashboard
        else:
            raise argparse.ArgumentTypeError(
                "Cannot parse string {0} for resourceType")
