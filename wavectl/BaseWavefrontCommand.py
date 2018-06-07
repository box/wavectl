
from __future__ import absolute_import
from __future__ import print_function
import re
import json
import os
import logging
import errno
import queue
import threading
import sys

from .BaseCommand import BaseCommand
from .Resource import Resource
from .ResourceFactory import ResourceFactory
from .Alert import Alert
from .Dashboard import Dashboard

import wavefront_api_client


class Error(Exception):
    pass


class BaseWavefrontCommand(BaseCommand):
    """ A base class for commands that talk to the WavefrontServer.
    For example show, pull, push"""

    concurrentThreadCount = 10

    @staticmethod
    def _addInGitOption(parser):
        parser.add_argument(
            "--inGit",
            "-g",
            action="store_true",
            help="""The given directory is source controlled with git. In this case
        the pull and push commands make use of git branches, do extra checks
        for modified files and detect conflicting remote-local changes.""")

    @staticmethod
    def _addRsrcTypeSubParsers(parser):
        """ The rsrcType subparser parses the match related, narrow down
        related parameters"""

        subParser = parser.add_subparsers(
            title="resourceType",
            description="Select the resource type to operate on",
            dest="rsrcType")
        subParser.required = True

        Alert.addSubparser(subParser)
        Dashboard.addSubparser(subParser)

    @staticmethod
    def _getRealPath(path):
        """ The path can be absolute or relative. Normalize the path and
        return the absolute path to the target. Throw an exception if the
        given path does not exist in the file system"""

        rp = os.path.realpath(path)
        p = os.path.abspath(rp)
        return p

    @staticmethod
    def _getRealDirPath(dirPath):
        """ The dirPath can be absolute or relative. Normalize the path and
        return the absolute path to the dir. Throw an exception if the
        given path is actually not a directory"""

        d = BaseWavefrontCommand._getRealPath(dirPath)
        if os.path.exists(d) and not os.path.isdir(d):
            raise Error("The given path: {} is not a dir".format(d))
        return d

    @staticmethod
    def _checkExpectedParameters(verb, **kwargs):
        """ Make sure that the kwargs contains the necessary parameters for the
        given request"""
        if verb == "post":
            assert "data" in kwargs

    @staticmethod
    def doesTermSupportColor():
        """Return true if the terminal supports coloring"""
        # The implementation is similar how grep implements --color=auto
        # http://superuser.com/a/497838
        t = os.environ.get("TERM")
        return sys.stdout.isatty() and t and t != "dumb"

    @staticmethod
    def getResourceFiles(rsrcType, d):
        """Return the absolute paths of the resource files of the given type in
        the given dir"""
        files = [x for x in [os.path.join(d, y) for y in os.listdir(d)]
                 if (os.path.isfile(x)
                     and x.endswith(rsrcType.fileExtension()))]
        return sorted(files)

    @staticmethod
    def searchAllRsrcsFromWavefront(searchF, body):
        """Wavefront search API is progressive. At every call it returns a limited
        number of rsrcs. In this function call the wavefront search api call
        repeatedly until we retrieve all matching rsrcs"""

        offsetKey = "offset"
        limit = 1000

        # Update the body with common parameters
        body["limit"] = limit
        body[offsetKey] = 0
        body["sort"] = {
            "field": "id",
            "ascending": True
        }

        rawRsrcs = []
        moreItems = True
        while moreItems:
            # With _preload_content the unmodified response is returned
            # as an HTTPResponse object.
            res = searchF(body=body, _preload_content=False)
            # Read into a dict.
            data = json.loads(res.read())
            # This object model is how the wavefront_api_client packs its
            # response.
            response = data["response"]
            rawRsrcs.extend(response["items"])
            body[offsetKey] = body[offsetKey] + limit
            moreItems = response["moreItems"]

        return rawRsrcs

    def getWavefrontHost(self):
        """Get the configured wavefronthost from the config file or command line"""
        if not self.config:
            self._getConfig()
        return self.config.get(BaseCommand.wavefrontHostKey)

    def getApiToken(self):
        """Get the configured apiToken from the config file or command line"""
        if not self.config:
            self._getConfig()
        return self.config.get(BaseCommand.apiTokenKey)

    def getWavefrontApiClient(self):
        """Crete and return the wavefrontApiClient object"""

        if self.wavefrontApiClient:
            return self.wavefrontApiClient

        host = self.getWavefrontHost()
        apiToken = self.getApiToken()

        config = wavefront_api_client.Configuration()
        config.host = host

        self.wavefrontApiClient = wavefront_api_client.ApiClient(
            configuration=config,
            header_name="Authorization",
            header_value="Bearer " + apiToken)

        return self.wavefrontApiClient

    def filterResources(self, rsrcType, rsrcs, args):
        """ Use the command line parameters further narrow down the
        resources the user wanted to process. Process the specified regular
        expressions"""

        regexes = {}

        # Get the argparse parameters namespace in dictionary
        # Even though the argparse subparsers add multiple levels of command
        # line parameters with different visibility, this vars function returns
        # a flattened dict of all command line parameters. Even the ones passed
        # in nested subparsers.
        argsDict = vars(args)

        # Inner list comprehension:
        # For each of the supported filters in rsrcType._supportedFilters, get its
        # value from the command line args if it has been specified. Otherwise
        # the argsDict.get will return None
        # Outer dictionary comprehension:
        # For each of the filters that was specified in the command line,
        # compile a regex and save it in the dictionary
        regexes = {
            k: re.compile(p) for (
                k, p) in [
                (f, argsDict.get(f)) for f in rsrcType._supportedFilters] if p}

        # Filter out the regexes that do not match the given regular expression
        # searches from the command line.
        m = argsDict.get("match")
        if m is not None:
            # If --match is specified, use it in an regex
            m = re.compile(m)
        filteredRsrcs = [
            rsrc for rsrc in rsrcs if rsrc.doAllRegexesMatch(regexes, m)]
        return filteredRsrcs

    def compileQueryList(self, customerTag):
        """The wavefront search API expects a well-formed list in the query list.
        Transform the entries in the customerTag list into a query list that
        the wavefront search api can use."""
        ql = []

        if customerTag is None:
            return ql

        for ct in customerTag:
            e = {
                "key": "tags.customerTags",
                "value": ct,
                "matchingMethod": "EXACT"
            }
            ql.append(e)

        return ql

    def getRsrcsViaWavefrontApiClient(self, rsrcType, customerTag, args):
        """Using the wavefront_api_client retrieve the given resources
        from the wavefront server.
        Return the list of objects representing resources state per entry.
        rsrcType: the Class that represents the resource. Alert, Dashboard etc.
        If self.designForTestRsrcs is specified, that means you are in test mode and
        directly return the set in designForTestRsrcs"""

        if self.designForTestRsrcs is not None:
            rsrcs = [rsrcType.fromDict(r) for r in self.designForTestRsrcs]
        else:
            apiClient = self.getWavefrontApiClient()
            getF = rsrcType.getFunction(apiClient)

            # The expected body parameters to the search api

            ql = self.compileQueryList(customerTag)
            searchBody = {
                "query": ql,
            }
            rawRsrcs = BaseWavefrontCommand.searchAllRsrcsFromWavefront(
                getF, searchBody)

            rsrcs = [rsrcType.fromDict(x) for x in rawRsrcs]
            logging.debug(
                "Received {} resources from wavefront are: {}".format(
                    len(rsrcs), rsrcs))

        remRsrcs = self.filterResources(rsrcType, rsrcs, args)
        logging.debug("Remaining {} resources after filtering are: {}".format(
            len(remRsrcs), remRsrcs))
        return remRsrcs

    def __init__(self, designForTestRsrcs=None, *args, **kwargs):
        super(BaseWavefrontCommand, self).__init__(*args, **kwargs)

        # For testability reasons, we may want to bypass the api server and use
        # our own alerts. This attribute can be used to bypass the wavefront api
        # server
        self.designForTestRsrcs = designForTestRsrcs
        self.wavefrontApiClient = None
