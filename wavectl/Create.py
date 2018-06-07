
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

# External dependencies:
import git

# TODO: The name is not correct anymore. It should be like
# WavefrontCmdImpl or something like that.
from .BaseWavefrontCommand import BaseWavefrontCommand
from .ResourceFactory import ResourceFactory
from .Mutator import Mutator
from .GitUtils import GitUtils

from .Alert import Alert


class CreateCommand(Mutator):
    """ The implementation of the `create` command. Used to post resource files
    from local dir to the remote wavefront server. This assumes that the wavefront
    resources do not exists in the wavefront server to start with"""

    def handleCmd(self, args):
        """ Handles the pull <resource> [...] commands.
        Reads the given resources from the given dir. Does filtering if necessary.
        Writes them back to the wavefront server"""

        super(CreateCommand, self).handleCmd(args)

        rsrcType = args.rsrcType
        parallelThreadCount = BaseWavefrontCommand.concurrentThreadCount

        rsrcs = self.doChecksGetRsrcsFromTarget(args)

        threadPool = multiprocessing.pool.ThreadPool(
            processes=parallelThreadCount)

        rsrcType = args.rsrcType
        rt = ResourceFactory.resourceTypeFromString(rsrcType)
        createFunction = rt.createFunction(self.getWavefrontApiClient())

        asyncResults = []
        for r in rsrcs:
            ar = threadPool.apply_async(
                Mutator.withApiExceptionRetry(createFunction),
                [],
                {"body": r._state, "_preload_content": False})
            asyncResults.append(ar)

        # TODO: How to handle mutateFunction exceptions in this pattern ?

        if not args.quiet:
            print("Created {}(s):".format(rsrcType))
            print(rt.summaryTableHeader())
        for ar in asyncResults:
            res = ar.get()
            data = json.loads(res.read())
            rawRsrc = data["response"]
            rsrc = rt.fromDict(rawRsrc)
            if not args.quiet:
                print(rsrc.summaryTableRow(
                    BaseWavefrontCommand.doesTermSupportColor()))

    def addCmd(self, subParsers):
        p = subParsers.add_parser(
            "create", help="create new resources in Wavefront using target")
        p.set_defaults(wavefrontConfigFuncToCall=self.handleCmd)
        self._addInGitOption(p)
        Mutator._addQuietOption(p)
        Mutator._addTargetOption(p)

        self._addRsrcTypeSubParsers(p)
        super(CreateCommand, self).addCmd(p)

    def __init__(self, *args, **kwargs):
        super(CreateCommand, self).__init__(*args, **kwargs)
