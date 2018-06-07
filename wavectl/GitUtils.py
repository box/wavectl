
# A common file to inlcude some frequently used git related tasks

from __future__ import absolute_import
from __future__ import print_function
import argparse
import os
import json
import time
import datetime
import sys
import tempfile
import shutil
import logging

# External dependencies:
import git


class GitUtils(object):
    @staticmethod
    def getExistingRepo(p):
        """ Verify that the given path is inside a git repository"""
        try:
            r = git.Repo(p, search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError as e:
            print("""The existing path {0} is not in a git repository. The
            `<cmd> <rsrcType> <existingPath> --inGit` expects to find
            <existingPath> in a git repository. The saved resource files should
            be source controlled in git. If you are trying to start a new repo
            from scratch, please pass a non-existing path to the
            command""".format(p))
            raise

        return r
