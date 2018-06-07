
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import json
import webbrowser

# External dependencies:
import termcolor

from .BaseWavefrontCommand import BaseWavefrontCommand
from .Resource import Resource
from .ResourceFactory import ResourceFactory

class ShowError(Exception):
    pass


class ShowCommand(BaseWavefrontCommand):
    """The implementation of the `show` command """

    _maxBrowserTabsEnvVarName = "MAX_BROWSER_TABS"

    @staticmethod
    def _maxBrowserTabs():
        """ Return the maximum number of browser tabs to spawn"""
        maxTabsStr = os.environ.get(
            ShowCommand._maxBrowserTabsEnvVarName, "10")
        try:
            rv = int(maxTabsStr)
        except ValueError:
            rv = 10

        return rv

    @staticmethod
    def _isTermColoringEnabled(color):
        """ Determines whether we will do any type of terminal coloring"""
        return color == ShowCommand.autoColor \
            and BaseWavefrontCommand.doesTermSupportColor()

    summaryOutput, jsonOutput = ["summary", "json"]

    @staticmethod
    def _addOutputOption(parser):
        """ -o --output, summary, json options."""
        parser.add_argument(
            "--output",
            "-o",
            choices=[
                ShowCommand.summaryOutput,
                ShowCommand.jsonOutput],
            default=ShowCommand.summaryOutput,
            help="""Output fromat.  summary output is default where one line is
            printed for each resource. Json prints out the full state of each
            resource in json form.""")

    def printSummaryTable(self, rsrcType, rsrcs, color, printHeader):
        """Print a nicely formatted summary table for all the resources.
        The summary table contains a single line summary for each resource."""

        # Print the header using the entryFormat
        if printHeader:
            print(rsrcType.summaryTableHeader())

        enableColor = ShowCommand._isTermColoringEnabled(color)
        for rsrc in rsrcs:
            print(rsrc.summaryTableRow(enableColor))

    def showResourcesInBrowser(self, rsrcs):
        """ Depending on the command line arguments and the number of selected
        resources , display the resources in a web browser. The user must
        specify --in-browser in the command line for us to launch a browser and
        the number of resources to display should be less than _maxBrowserTabs.
        We do not want to create 100's of tabs programmatically by accident"""

        if len(rsrcs) == 0:
            return

        if len(rsrcs) > ShowCommand._maxBrowserTabs():
            raise ShowError(
                "Too many resources to display in browser. Selected " +
                "resrouces: {0}, maximum supported {1}"
                "".format(
                    len(rsrcs),
                    ShowCommand._maxBrowserTabs))

        # Open the first resource in a new window.
        # Then open the rest of the resources in tabs.
        # TODO: The python documentation does not guarantee the new window
        # and tab usage. All new pages can be opened in new tabs.
        rsrc = rsrcs[0]
        urlPrefix = self.getWavefrontHost()
        webbrowser.open_new(urlPrefix + rsrc.browserUrlSuffix())
        for rsrc in rsrcs[1:]:
            webbrowser.open_new_tab(urlPrefix + rsrc.browserUrlSuffix())

    def handleCmd(self, args):
        """ Handles the show [...] commands."""
        super(ShowCommand, self).handleCmd(args)

        rsrcType = args.rsrcType
        rt = ResourceFactory.resourceTypeFromString(rsrcType)

        rsrcs = self.getRsrcsViaWavefrontApiClient(rt, args.customerTag, args)

        if args.output == ShowCommand.summaryOutput:
            self.printSummaryTable(rt, rsrcs, args.color, not args.noHeader)
        elif args.output == ShowCommand.jsonOutput:
            for r in rsrcs:
                print(r.jsonStr())
        else:
            assert not "Unexpected output option in args."

        if args.inBrowser:
            self.showResourcesInBrowser(rsrcs)

    autoColor, neverColor = ("auto", "never")

    def _addColorOption(self, parser):
        parser.add_argument(
            "--color",
            "-l",
            choices=[
                self.autoColor,
                self.neverColor],
            default="auto",
            help="""Enable/Disable colored output in the summary table.
        If set to auto the output will be colored if the terminal supports it.
        If set to never, ouput will not be colored""")

    def _addInBrowserOption(self, parser):
        parser.add_argument(
            "--in-browser",
            "-b",
            dest="inBrowser",
            action="store_true",
            help="""Open the selected resources in the default browser in new
            tabs. At most {0} new tabs are supported. If the selected number
            of resources are more than {0}, an exception is thrown. The
            supported max can be changed by setting the {1} env
            var""".format(
                ShowCommand._maxBrowserTabs(),
                ShowCommand._maxBrowserTabsEnvVarName))

    def _addNoHeaderOption(self, parser):
        parser.add_argument(
            "--no-header",
            dest="noHeader",
            action="store_true",
            help="""If set, the show command does not print the table header in
            summary mode""")

    def addCmd(self, subParsers):
        p = subParsers.add_parser(
            "show", help="""show prints Wavefront rsrcs in
            various formats """)
        p.set_defaults(wavefrontConfigFuncToCall=self.handleCmd)

        ShowCommand._addOutputOption(p)
        self._addColorOption(p)
        self._addInBrowserOption(p)
        self._addNoHeaderOption(p)

        self._addRsrcTypeSubParsers(p)

        super(ShowCommand, self).addCmd(p)

    def __init__(self, *args, **kwargs):
        super(ShowCommand, self).__init__(*args, **kwargs)
