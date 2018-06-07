#!/usr/bin/env python

# This file contains negative tests for the push command.

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
# Extend that path so that we can import the module under test.
sys.path.insert(0, os.path.abspath('..'))

# Design under test.
import wavectl

import unittest
import tempfile
import git
import shutil
import copy
import json
import time

import util


class Test(util.TestPullMutate):
    """ A class that checks for error conditions in the `create` command"""


if __name__ == '__main__':
    util.unittestMain()

# Test Plan
# Try to create an existing resource. The user should use update(push for now)
# instead
