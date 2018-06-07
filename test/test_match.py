#!/usr/bin/env python

# This file contains positive tests for regular expression matching/filtering of
# alerts.

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

import git

import util


class Test(unittest.TestCase):
    """ A test suite for the regex matching comparisons in the wavectl command.
    Wavectl provides bunch of options to filter the alerts. In this type
    we excerise that code."""

    def test_match(self):
        #  testData = [
            #  (),
        #  ]
        pass

#  TestPlan
#  1) Add a test for a selector but the selector does not exist for a particular
#  resource. For example the command line client has specified --updaterId
#  as a selector. However some resources do not have that key.
#  If the key does not exist, we should not throw an exception but not select
#  the resource.


if __name__ == '__main__':
    util.unittestMain()
