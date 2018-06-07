
from __future__ import absolute_import
from __future__ import print_function
import argparse
import sys
import logging
import http.client

import argcomplete

from .Config import ConfigCommand
from .Show import ShowCommand
from .Pull import PullCommand
from .Push import PushCommand
from .Create import CreateCommand

from .Resource import Resource

import wavefront_api_client


class Wavectl(object):

    @staticmethod
    def enableChildLogger(loggerName, fmtString, level):
        """Get the logger interface by name and enable it with the given level"""

        childLogger = logging.getLogger(loggerName)

        # Add a handler so we have the output formatter to our liking.
        handler = logging.StreamHandler()  # By default the output goes to stderr
        handler.setFormatter(logging.Formatter(fmtString))
        childLogger.addHandler(handler)

        childLogger.setLevel(level)
        # The child logger has an handler already. No need to propagate further
        # to parent loggers.
        childLogger.propagate = False

    @staticmethod
    def initLog(level):
        """Init the basic logging"""

        # TODO: We should instantiate a logger here and set its parameters.
        fmtString = "%(asctime)s %(process)d %(threadName)s %(name)s " \
            + "%(levelname)s %(message)s"
        logging.basicConfig(
            format=fmtString,
            stream=sys.stderr,
            level=level)

        # TODO: wavefront_api_client.Configuration() constructor clears the
        # HTTPConnection.debuglevel flag. This may turned off later on.
        if level <= logging.DEBUG:
            http.client.HTTPConnection.debuglevel = 1

        Wavectl.enableChildLogger("wavefront_api_client", fmtString, level)
        Wavectl.enableChildLogger("urllib3", fmtString, level)
        Wavectl.enableChildLogger(
            "wavefront_api_client.rest", fmtString, level)

    def __init__(
            self,
            designForTestArgv=None,
            designForTestRsrcs=None,
            designForTestConfigDir=None):
        """
        designForTestArgv: In unit tests, one can overwrite the command
        line arguments for better testability.
        designForTestRsrcs: One can make the Wavefront class bypass reaching out
        the wavefront api server and directly use the given alert list
        """

        parser = argparse.ArgumentParser(
            prog="wavectl",
            description="A command line tool to programmatically interact "
            + "with wavefront")

        parser.add_argument(
            "--log",
            default="WARNING",
            choices=[
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL"],
            help="""Set the logging level for the command""")

        subParsers = parser.add_subparsers(
            title="subcommands",
            description="Choose a subcommand to execute",
            dest="subcommands")
        subParsers.required = True

        # For each new command, add a new call here
        # TODO: Is there a more automatic/pythonic way of doing this ?
        self.config = ConfigCommand(
            designForTestConfigDir=designForTestConfigDir)
        self.config.addCmd(subParsers)

        self.show = ShowCommand(
            designForTestRsrcs=designForTestRsrcs,
            designForTestConfigDir=designForTestConfigDir)
        self.show.addCmd(subParsers)

        self.pull = PullCommand(
            designForTestRsrcs=designForTestRsrcs,
            designForTestConfigDir=designForTestConfigDir)
        self.pull.addCmd(subParsers)

        self.push = PushCommand(designForTestConfigDir=designForTestConfigDir)
        self.push.addCmd(subParsers)

        self.create = CreateCommand(
            designForTestConfigDir=designForTestConfigDir)
        self.create.addCmd(subParsers)

        # You need to execute
        # eval "$(register-python-argcomplete wavectl)"
        # for the autocompletion to effect.
        argcomplete.autocomplete(parser)

        self.args = parser.parse_args(args=designForTestArgv)

        Wavectl.initLog(getattr(logging, self.args.log))

    def runCmd(self):
        """ Executes the function that handles the operation described by the
        command line arguments"""

        # TODO: This is a design for testability addition. Normally the static list
        # in the Resource type will always be empty at the start.
        # However during tests, we re-use the same instance to execute multiple
        # test scenarios. This cleanup serves as deleting the state from the
        # previous test run.
        Resource.allRsrcs = []
        Resource._summaryTableFormat = {
            True: None,
            False: None,
        }

        self.args.wavefrontConfigFuncToCall(self.args)
