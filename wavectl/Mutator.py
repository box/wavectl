
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
import threading
import multiprocessing
import types
import urllib3
import http.client

# External dependencies:
import git
import wavefront_api_client

# TODO: The name is not correct anymore. It should be like
# WavefrontCmdImpl or something like that.
from .BaseWavefrontCommand import BaseWavefrontCommand
from .GitUtils import GitUtils
from .ResourceFactory import ResourceFactory


class MutatorError(Exception):
    pass


class Mutator(BaseWavefrontCommand):
    """ The implementation of the common functions in the Push and Create
    commands."""

    @staticmethod
    def _addQuietOption(parser):
        parser.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            help="""Supress printed output about mutated resrouces.""")

    @staticmethod
    def _addTargetOption(parser):
        parser.add_argument("target", help="""Wavefront resource data from this
        target will be written to the wavefront server. target can be a path to
        a directory or a file. For directories all resource files in that
        directory will be considered. For files, on the that file is considered
        for a push""")

    @staticmethod
    def withApiExceptionRetry(wavefrontFunction):
        """A decorator to call the given function in a retry loop. If the function
        raises a wavefront_api_client.ApiException, the exception gets logged
        and the function is retried"""

        def rv(*args, **kwargs):
            retries = 3
            while True:
                try:
                    res = wavefrontFunction(*args, **kwargs)
                except (wavefront_api_client.rest.ApiException,
                        http.client.BadStatusLine,
                        http.client.HTTPException,
                        urllib3.exceptions.ProtocolError,
                        Exception) as e:

                    logging.debug(
                        ("Received exception with type {} from api call:"
                         "{}Retries: {}").format(
                            type(e), e, retries))
                    retries = retries - 1

                    # In case we receive bunch of consecutive exceptions,
                    # raise the exception after exhaustion of retires.
                    if retries == 0:
                        raise

                    # If the Api server has returned with some error, give some time
                    # before retrying.
                    time.sleep(0.1)
                else:
                    return res

        return rv

    def checkCleanDirInRepo(self, r, d):
        """ Check that the given dir in the git repo is "clean". In other words,
        there are no staged or modified files in the given directory."""
        if r.is_dirty(path=d):
            raise MutatorError(
                ("The path at {0} is dirty. Please commit your outstanding changes "
                 "and try again... \n{1}").format(
                    r.working_tree_dir, r.git.status(d)))

    def filterRsrcsWrtTag(self, rsrcs, customerTag):
        """We filter the resoruces according to their customerTag field.  For the
        filtering of resources received from the wavefront server, we did not
        process the customerTags locally. Because the server already does the
        customerTag filtering. For the resources that are read from a local
        directory, we additionally need to filter them using the customerTag
        filed."""

        if customerTag is None:
            # The user has not specified any customerTag. So all rsrcs are
            # matching
            return rsrcs

        assert(len(customerTag) > 0
               and "Expected valid entries in the customerTag parameter")

        rv = [r for r in rsrcs if r.doesContainAllTags(customerTag)]
        return rv

    def getRsrcFromFile(self, rsrcType, fn):
        """Given the full file path, return the rsrc object for it.
        The return value can be Alert or Dashboard etc."""

        with open(fn) as f:
            r = rsrcType.fromDict(json.load(f))
        return r

    def getRsrcsFromPath(self, rsrcType, p, customerTag, args):
        """Parse all the resource files in the given dir or parse the file at
        the given path , filter them according to the user's command line
        params and return a list of them"""

        # The passed parameter can be a directory or a file.
        # In case of a directory all resource files in it will be parsed.
        # In case of a file, only that file will be parsed.
        if os.path.isdir(p):
            files = BaseWavefrontCommand.getResourceFiles(rsrcType, p)
            rsrcs = []
            for fn in files:
                r = self.getRsrcFromFile(rsrcType, fn)
                rsrcs.append(r)
        else:
            rsrc = self.getRsrcFromFile(rsrcType, p)
            rsrcs = [rsrc]

        remRsrcs = self.filterRsrcsWrtTag(rsrcs, customerTag)
        remRsrcs = self.filterResources(rsrcType, remRsrcs, args)
        return remRsrcs

    def doChecksGetRsrcsFromTarget(self, args):
        """Execute necessary checks and get the resources from the args.target.
        Do necessary filtering as specified by the user."""

        p = self._getRealPath(args.target)
        if not os.path.exists(p):
            # For create and push commands (mutators) the passed target
            # should exist in the file system.
            raise MutatorError("The given path: {} does not exist".format(p))

        rsrcType = args.rsrcType
        rt = ResourceFactory.resourceTypeFromString(rsrcType)
        if args.inGit:
            r = GitUtils.getExistingRepo(p)
            self.checkCleanDirInRepo(r, p)

        rsrcs = self.getRsrcsFromPath(rt, p, args.customerTag, args)

        logging.info("Using the resources: [{0}] from path: {1}".format(
            " ".join([str(r.uniqueId()) + rt.fileExtension() for r in rsrcs]), p))

        return rsrcs

    def __init__(self, *args, **kwargs):
        super(Mutator, self).__init__(*args, **kwargs)
