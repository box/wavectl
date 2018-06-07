#!/usr/bin/env python

# Alert state used for tests.


from __future__ import absolute_import
from __future__ import print_function

import json


class Rsrc(object):
    """ Base class for alert dashboard, etc data used for tests """

    @staticmethod
    def getTestRsrcs(fileName):
        """Get the resources in the passed json file and return them as a list"""
        # TODO: These file lookups should be cached.
        with open(fileName) as f:
            rv = json.load(f)
        return rv

    @staticmethod
    def appendToKey(s, k, d):
        """Append the string s to the name key in the dictionary d"""
        d[k] = d[k] + s
        return d
