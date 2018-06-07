
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


class PushCommand(Mutator):
    """ The implementation of the `push` command. Used to post resource files
    from local dir to the remote wavefront server"""

    def handleCmd(self, args):
        """ Handles the pull <resource> [...] commands.
        Reads the given resources from the given dir. Does filtering if necessary.
        Writes them back to the wavefront server"""

        super(PushCommand, self).handleCmd(args)

        rsrcs = self.doChecksGetRsrcsFromTarget(args)

        threadPool = multiprocessing.pool.ThreadPool(
            processes=BaseWavefrontCommand.concurrentThreadCount)

        rsrcType = args.rsrcType
        rt = ResourceFactory.resourceTypeFromString(rsrcType)
        updateFunction = rt.updateFunction(self.getWavefrontApiClient())

        asyncResults = []
        for r in rsrcs:
            ar = threadPool.apply_async(
                Mutator.withApiExceptionRetry(updateFunction),
                [r.uniqueId()],
                {"body": r._state, "_preload_content": False})
            asyncResults.append(ar)

        # TODO: How to handle mutateFunction exceptions in this pattern ?

        if not args.quiet:
            print("Replaced {}(s):".format(rsrcType))
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
            "push", help=(
                "push resource files from the given target to "
                " Wavefront"))
        p.set_defaults(wavefrontConfigFuncToCall=self.handleCmd)
        self._addInGitOption(p)
        Mutator._addQuietOption(p)
        Mutator._addTargetOption(p)

        self._addRsrcTypeSubParsers(p)

        super(PushCommand, self).addCmd(p)

    def __init__(self, *args, **kwargs):
        super(PushCommand, self).__init__(*args, **kwargs)
