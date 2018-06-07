#!/usr/bin/env python

# Common utils and data for test files


from __future__ import absolute_import
from __future__ import print_function

try:
    # Python 2
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import __main__
import sys
import os
import re
import datetime
import time
import unittest
import socket
import socketserver  # requires future module for python2
import http.server  # requires future module for python2
import threading
import json
import tempfile
import shutil
import collections
import copy
import six
import logging
import random
import traceback
import warnings
if six.PY3:
    import unittest.mock as mock
else:
    import mock


import wavefront_api_client

import wavectl
from wavectl.BaseWavefrontCommand import BaseWavefrontCommand
from wavectl.Mutator import Mutator
import TestAlerts

import git
import TestDashboards

from TestAlerts import Alert
from TestDashboards import Dashboard


wavefrontHostName = "https://try.wavefront.com"
wavefrontApiToken = "DEAD-BEEF"  # Does not matter just some string.


def initLog():
    """Initialize the logging.
    Expected to be called from tests. Test function would like to log something"""
    wavectl.Wavectl.initLog(logging.DEBUG)


def checkListEqual(l1, l2):
    """ If we cannot call unittest.TestCase.assertListEqual for some reason,
    we can use this function to compare lists instead. We may not be getting a nice
    summarized error message but this is better than nothing"""
    return len(l1) == len(l2) and sorted(l1) == sorted(l2)


def resourceTypeFromString(rsrcType):
    """Get the string representation of a resource an return the python type
    instance for that class"""
    rv = wavectl.ResourceFactory.ResourceFactory.resourceTypeFromString(
        rsrcType)
    return rv


class EnvModifier(object):
    """ A context manager class used to modify the enviornment."""

    def __init__(self, envVar, val):
        """ Save the environment variable to change and its desired value """
        self.envVar = envVar
        self.var = val
        self.oldVar = None

    def __enter__(self):
        """ Modify the given envVar to the new value"""
        self.oldVar = os.environ.get(self.envVar)

        if self.var is not None:
            os.environ[self.envVar] = self.var
        else:
            try:
                del os.environ[self.envVar]
            except KeyError:
                pass

    def __exit__(self, type, value, traceback):
        """ Restore the env var to the old value"""
        if self.oldVar is None:
            """ Env var did not exist before. Delete it again"""
            try:
                del os.environ[self.envVar]
            except KeyError:
                pass
        else:
            os.environ[self.envVar] = self.oldVar

        return False


class TempDir(object):
    """ A class that creates a temp directory at context creation time and
    removes the temp dir at exit of the context."""

    def __init__(self, retain=False):
        # For debuggability, if retain is True, do not delete the temp dir
        self.retain = retain

    def __enter__(self):
        self.d = tempfile.mkdtemp()
        logging.debug("Using temporary directory: {}".format(self.d))
        return self

    def dir(self):
        return self.d

    def __exit__(self, type, value, traceback):
        if self.retain:
            msg = "TempDir: {0}".format(self.d)
            logging.debug(msg)
            print(msg)
        else:
            shutil.rmtree(self.d, ignore_errors=True)

        return False


class DummyContextManager(object):
    """ A context manager that does not do anything. Used to implement
    conditional context managers like here:
    https://stackoverflow.com/a/27806978/5771861"""

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        return False


class CwdChanger(object):
    """ A class that changes to the given directory at context manager creation
    time.  At the context exit it restores the original working dir"""

    def __init__(self, desiredDir):
        self.desiredDir = desiredDir

    def __enter__(self):
        self.originalDir = os.getcwd()
        os.chdir(self.desiredDir)

    def __exit__(self, type, value, traceback):
        os.chdir(self.originalDir)
        return False


class StdoutCapture(object):
    """ A class that can be used in with statements to overwrite the std out
    in its context.
    This object can be used together with "with" statements For example:

    with util.StdoutCapture() as capturedOut:
        print "Capture this line"
    assert capturedOut.str().strip()=="Capture this line".strip()
    """

    def __init__(self, ignore=False):
        # Ignore make this capture a no-op. For easy debugging.
        self.ignore = ignore
        self.strIo = StringIO()

    def __enter__(self):
        """ Overwrite the sys.strout with an internally saved StringIO object.
        This way we can capture the print statement of the function under
        test and verity them later on. """
        if not self.ignore:
            self.origStdout = sys.stdout
            sys.stdout = self.strIo
        return self

    def __exit__(self, type, value, traceback):
        """Restore the sys.stdout to its original value"""
        if not self.ignore:
            sys.stdout = self.origStdout
        return False

    def str(self):
        """Return the captures sys.out in a string"""
        return self.strIo.getvalue()


class StdinRedirect(object):
    """A class that can redirect the given StringIO to the stdin of the program.
    This type is expected to be used in context managers. A already populated
    stream (e.g: StringIo) type should be passed at construction time"""

    def __init__(self, newStdin):
        newStdin.seek(0)
        self.newStdin = newStdin

    def __enter__(self):
        self.origStdin = sys.stdin
        sys.stdin = self.newStdin
        return self

    def __exit__(self, type, value, traceback):
        sys.stdin = self.origStdin
        return False


class SummaryLineProcessor(object):
    """A class that contains functions to process summary lines. Used by
    craete and show tests"""

    @staticmethod
    def expectedAlertSummaryLineRegex(a, ignoreStatus=False):
        """ Given an alert, return a regular expression that should match that
        alert's summary line
        if ignoreStatus is passed, the status field value is made optional
        """

        # During write created field changes. It is a timestamp. So have a
        # numerical regex instead.
        rv = r"\d+\s*" \
            + re.escape(a["name"]) + r"\s*(NO_DATA)?\s*" \
            + (r"(" if ignoreStatus else r"") \
            + r"(NO_DATA)?\s*".join(a["status"]) + r"\s*(NO_DATA)?\s*" \
            + (r")?" if ignoreStatus else "") \
            + re.escape(a["severity"])
        return rv

    @staticmethod
    def expectedDashboardSummaryLineRegex(d):
        """ Given a dashboard, return a regular expression that should match that
        dashboard's summary line"""
        rv = re.escape(d.get("url", "")) + r"\s*" \
            + re.escape(d.get("name", "")) + r"\s*" \
            + re.escape(d.get("description", ""))
        return rv

    @staticmethod
    def compareExpectedActualLineByLine(test, expectedOutRegex, actualOut):
        """ The expectedOutRegex and the actualOut are given in a list form
        where each entry in actualOut is a line. The correponding entry (same
        index) in expectedOutRegex is a reqular expression for the same line to
        match.  This function compares checks that every line matches its
        regular expression."""

        test.assertEqual(len(expectedOutRegex), len(actualOut))

        regexes = [re.compile(e) for e in expectedOutRegex]
        for a in actualOut:
            # Each line in actualOut should match with at least one regex in
            # expectedOut.
            # TODO: We could be more strict about the matching. We could purge
            # the regular expression once a line has been matched against it.
            compRes = [regex.match(a) for regex in regexes]
            if not any(compRes):
                logging.debug(
                    "Rsrc line did not match any regular expressions:\n" +
                    "Rsrc:\n{}\nRegularExpressions:\n{}".format(
                        str(a),
                        "\n".join(expectedOutRegex)))
                test.assertTrue(not "Could not find summary line in regexes")


def mockRsrcType(rsrcType, rsrcs, deletedRsrcs):
    """Given a rsrcType, mock its getFunction.
    With this we can mock what the API server would return back to the
    wavectl client. For example the Alert.getFunction returns the
    wavefront_api_client.api_client.search_alert_entities function
    that reaches out to wavefront server. With mocking the Alert.getFunction,
    we return our custom function that returns the rsrcs without reaching out
    to the api server"""

    def wavefrontSearchHttpResponse(items):
        """Return an HttpResponse object that looks like what is returned by
        searchApi.search_alert/dashboard_entities functions"""
        class MockHttpResponse(object):
            def read(*args, **kwargs):
                data = {
                    "response": {
                        "moreItems": False,
                        "items": sorted(items, key=lambda x: x["id"]),
                    }
                }
                return json.dumps(data)
        return MockHttpResponse()

    def mockSearchRsrcEntities(**kwargs):
        body = kwargs["body"]
        ql = body["query"]
        tags = [q["value"] for q in ql]
        filteredRsrcs = [r for r in rsrcs if all(
            [(t in r["tags"]["customerTags"]) for t in tags])]
        return wavefrontSearchHttpResponse(filteredRsrcs)

    def mockSearchRsrcDeletedEntities(**kwargs):
        return wavefrontSearchHttpResponse(deletedRsrcs)

    def wavefrontSingletonHttpResponse(rsrc):
        """Return an HttpResponse object that looks like what is returned by
        alert/dashabordApi.create/update_alert/dashboard functions"""
        class MockHttpResponse(object):
            def read(*args, **kwargs):
                data = {
                    "response": rsrc
                }
                return json.dumps(data)
        return MockHttpResponse()

    def mockSingleton(*args, **kwargs):
        body = kwargs["body"]
        return wavefrontSingletonHttpResponse(body)

    m = mock.MagicMock()
    m.return_value = mockSearchRsrcEntities
    rsrcType.getFunction = m

    m = mock.MagicMock()
    m.return_value = mockSearchRsrcDeletedEntities
    rsrcType.getDeletedFunction = m

    m = mock.MagicMock()
    m.return_value = mockSingleton
    rsrcType.createFunction = m
    rsrcType.updateFunction = m


class Test(unittest.TestCase):

    @staticmethod
    def mockAllRsrcTypes():
        logging.debug("Starting Test class")

        testAlerts = TestAlerts.Alert.getTestAlerts()
        testDashboards = TestDashboards.Dashboard.getTestDashboards()

        mockRsrcType(wavectl.Alert.Alert, testAlerts, [])
        mockRsrcType(wavectl.Dashboard.Dashboard, testDashboards, [])

    @staticmethod
    def _setUp():
        #  In python3, the urllib3 library may raise these socket resource
        #  warnings. They should be benign and an artifact of a performance
        #  optimization of reusing the sockets.
        #  https://github.com/mementoweb/py-memento-client/issues/6#issuecomment-196381413
        if six.PY3:
            warnings.filterwarnings(
                "ignore",
                message="unclosed <ssl.SSLSocket",
                category=ResourceWarning)

    def setUp(self):
        """A function that is called before every test function execution"""
        Test._setUp()
        logging.debug("Starting test {}".format(self._testMethodName))
        Test.mockAllRsrcTypes()

    def tearDown(self):
        logging.debug("Finishing test {}".format(self._testMethodName))

    def getCompareKeys(self, rsrcType):
        """Return the keys used to compare two different resource instances
        of the same time. For example compare two alert states. Various individual
        fields of resources are not always stable. Some of them are arbitrary or
        sometimes randomly change. For a stable comparison operation, we only
        select a subset of the keys."""

        # TODO: This comparison of subset of keys  logic could move to a __eq__
        # function in the Alert Dashboard time itself.

        if rsrcType == "alert":
            compareKeys = [
                "additionalInformation",
                "condition",
                "displayExpression",
                "minutes",
                "name",
                "severity",
            ]
        elif rsrcType == "dashboard":
            compareKeys = ["name", "parameters", "description"]
            pass
        else:
            assert not "Unexpected rsrcType"

        return compareKeys

    def compareRsrcs(self, r1, r2, compareKeys):
        """ Return that the compareKeys in r1 and r2 are equal to each other"""
        compK = set(compareKeys)
        visitedKeys = 0
        for k1, v1 in r1.items():
            if k1 in compK:
                visitedKeys = visitedKeys + 1
                v2 = r2.get(k1, "")
                if v1 != v2:
                    return False

        # If a key was missing in both the r1 and r2, they are considered equal too.
        # Look at keys that are missing in both and consider them as visited
        for k in compK:
            foundIn1 = r1.get(k)
            foundIn2 = r2.get(k)
            if foundIn1 is None and foundIn2 is None:
                visitedKeys = visitedKeys + 1

        # If we are returning true make sure that we have really compared all
        # keys.
        assert(visitedKeys == len(compK)
               and "Not all compareKeys were considered")
        return True


class TestPullMutate(Test):
    """ Common functions used in Pull and Push test suites"""

    def repoInit(self, d):
        """Initialize a git repo in the given dir and return its reference"""
        r = git.Repo.init(d)
        r.git.config("user.email", "you@example.com")
        return r

    def addReadmeFileToRepo(self, r):
        """ Adds a README.md file to the given repo"""
        d = r.working_tree_dir
        n = "README.md"
        p = os.path.join(d, n)
        with open(p, "w") as f:
            f.write("This is a repo to manage wavefront resources.")
        r.index.add([p])
        r.index.commit("Initial commit with the README.md file")

    def addNewFileToRepo(self, r, n, subdir=""):
        """Adds a new file named "n" to the index in the repo. By default the
        file is localted at the root dir. If the relative  subdir is given,
        the file is placed in that subdir. Does not commit the addition"""
        d = r.working_tree_dir
        p = os.path.join(d, subdir, n)

        # Create the file
        with open(p, "w") as f:
            pass
        r.index.add([p])

    def existingRepoDirNotGit(self, cmd, rsrcType, rsrcs):
        """ The repoDir is an existing directory however it is not a source
        controlled directory. The pull resource  command should raise an exception"""

        with TempDir() as td:
            d = td.dir()
            args = [cmd, d, "--inGit", rsrcType]
            wc = wavectl.Wavectl(
                designForTestArgv=args,
                designForTestRsrcs=rsrcs)
            self.assertRaises(
                git.exc.InvalidGitRepositoryError,
                wc.runCmd)

    def repoIndexIsDirtyInUsedDir(self, cmd, rsrcType, rsrcs, error):
        """In this testcase, the repo has staged changes that have not been
        committed yet in the same dir as the pull/push dir. The command should
        not allow this to happen. We expect the initial branch to be without any
        outstanding modifications"""

        with TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            self.addNewFileToRepo(r, "newFile")

            args = [cmd, d, "--inGit", rsrcType]

            wc = wavectl.Wavectl(
                designForTestArgv=args,
                designForTestRsrcs=rsrcs)

            self.assertRaisesRegexp(
                error,
                (r"The path at .+ is dirty. "
                 r"Please commit your outstanding changes .*"),
                wc.runCmd)

    def repoWorkingTreeIsDirtyInUsedDir(self, cmd, rsrcType, rsrcs, error):
        """ Git repo has local modifications to tracked files that have not
        been staged yet in the same dir as the pull/push dir. The working tree is
        dirty. The command should not allow a pull or a push to execute in this
        state"""

        with TempDir() as td:
            d = td.dir()
            r = self.repoInit(d)

            self.addReadmeFileToRepo(r)
            n = "newFile"
            self.addNewFileToRepo(r, n)

            r.index.commit("Initial commit of {} file".format(n))

            # After committing the following changes will be local modification that
            # are not staged yet.
            fn = os.path.join(d, n)

            with open(fn, "r+") as f:
                f.write("Some new modification")

            args = [cmd, d, "--inGit", rsrcType]
            wc = wavectl.Wavectl(
                designForTestArgv=args,
                designForTestRsrcs=rsrcs)

            self.assertRaisesRegexp(
                error,
                (r"The path at .+ is dirty. "
                 r"Please commit your outstanding changes .*"),
                wc.runCmd)

    def checkRsrcFilesInDir(
            self,
            rsrcType,
            rsrcs,
            dir,
            additionalFileNames=[]):
        """Check that the files for the given resources exist in the given dir"""

        # Clean up the given dir.
        d = os.path.realpath(dir)

        rt = resourceTypeFromString(rsrcType)

        expFiles = sorted(additionalFileNames +
                          [str(r[rt._uniqueKey]) +
                           rt.fileExtension() for r in rsrcs])

        # Get the basenames of the files in repo and discard directories
        actFiles = sorted([os.path.basename(f) for f in os.listdir(d)
                           if os.path.isfile(os.path.join(d, f))])
        self.assertListEqual(expFiles, actFiles)

    def checkFilesInDir(self, rsrcType, rsrcs, dir, additionalFileNames=[],
                        ignoredKeys=[]):
        """Compares the resources in the given rsrcs list with the resource files
        in the given directory.
        Read the json from the files in the dir, compare their state with the
        given expected rsrcs. Also ensure that the given addiitonalFileNames
        also exist in the dir.
        If ignored keys are given, the comparison of the resource with the file
        contents ignores those keys. """

        d = os.path.realpath(dir)

        rt = resourceTypeFromString(rsrcType)

        # contains the full paths of files
        actFilePaths = sorted(
            [p for p in [os.path.join(d, f) for f in os.listdir(d)]
                if os.path.isfile(p)])

        actRsrcs = []
        actAdditionalFilesNames = []
        for p in actFilePaths:
            if p.endswith(rt.fileExtension()):
                # This is a resource file. Alerts or Dashboards
                with open(p) as f:
                    actR = json.load(f)
                    actRsrcs.append(actR)
            else:
                # This is an extra file.
                actAdditionalFilesNames.append(os.path.basename(p))

        if len(actRsrcs) != len(rsrcs):
            logging.debug(
                ("actRsrcs ({}) and rsrc ({}) are not the same length\n"
                 "actRsrcs:\n{}\nrsrcs:\n{}").format(
                    len(actRsrcs), len(rsrcs), actRsrcs, rsrcs))
            self.assertTrue(not "actRsrc and rsrcs length mismatch")

        compareKeys = self.getCompareKeys(rsrcType)

        # TODO: We could have sorted these two resource lists by "name" and then
        # did a simpler comparison.
        for r1 in rsrcs:
            foundMatchingRsrc = any(
                [self.compareRsrcs(r1, r2, compareKeys) for r2 in actRsrcs])
            if not foundMatchingRsrc:
                logging.info(
                    ("The could not find the equivalent of resource: \n"
                     "{}\n").format(
                        r1, r2))
            self.assertTrue(foundMatchingRsrc)

        self.assertListEqual(sorted(actAdditionalFilesNames),
                             sorted(additionalFileNames))

    def executePull(
            self,
            rsrcType,
            dir,
            repo,
            expectedRsrcsInDir,
            pullAdditionalParams=[],
            rsrcAdditionalParams=[],
            additionalFileNames=[]):
        """ Execute a pull operation while some api functions are mocked."""

        logging.info("Starting executePull")

        args = ["pull",
                dir,
                "--wavefrontHost", wavefrontHostName,
                "--apiToken", wavefrontApiToken] \
            + pullAdditionalParams \
            + [rsrcType] \
            + rsrcAdditionalParams

        wc = wavectl.Wavectl(designForTestArgv=args)
        wc.runCmd()

        try:
            git.Repo(dir)
        except git.exc.InvalidGitRepositoryError as e:
            readmeFile = []
        else:
            readmeFile = ["README.md"]

        self.checkFilesInDir(
            rsrcType,
            expectedRsrcsInDir,
            dir,
            additionalFileNames=additionalFileNames + readmeFile)

        if repo:
            self.assertTrue(not repo.is_dirty(
                untracked_files=(len(additionalFileNames) == 0)))
            self.assertListEqual(sorted(repo.untracked_files),
                                 sorted(additionalFileNames))

        logging.info("Completed executePull")


class TestPull(TestPullMutate):
    """A base class to be used from test_pull and test_pullErrors"""

    def createPullBranch(self, r, fmt, suffix):
        """Creates pull branch in the given repo as expected from the Wavefront
        if it does not exist already"""
        minDate = datetime.datetime.fromtimestamp(time.mktime(time.gmtime(0)))
        pbn = minDate.strftime(fmt) + suffix

        try:
            r.heads[pbn]
        except IndexError as e:
            # If you cannot find the pull branch name, create one  so that
            # future pulls can checkout from thay branch.
            r.heads.master.checkout(b=pbn)
            # switch back to the master branch to leave the repo in an
            # expected state
            r.heads.master.checkout()


class TestMutate(TestPullMutate):
    """A class to be used from test_pull and test_create"""

    def compareRsrcsInDirs(
            self,
            rsrcType,
            pushedDir,
            pulledDir,
            expUnequalRsrcs):
        """Compare the resources in the two directories.
        pushedDir and pulledDir should be two distinct directories with resource
        files in them. PushedDir is used to write to the wavefront server (using
        push or create). PulledDir is used to read from the wavefront server.
        The resources mentioned in the expUnequalRsrc should be mismatching
        in the pushed and pulledDir"""

        rt = resourceTypeFromString(rsrcType)
        expUnequalUniqueIds = set([r[rt._uniqueKey] for r in expUnequalRsrcs])

        pushedRsrcFiles = BaseWavefrontCommand.getResourceFiles(rt, pushedDir)
        pulledRsrcFiles = BaseWavefrontCommand.getResourceFiles(rt, pulledDir)

        self.assertEqual(len(pushedRsrcFiles), len(pulledRsrcFiles))

        for pushedFile, pulledFile in zip(pushedRsrcFiles, pulledRsrcFiles):
            # Open both files and ensure that their string contents are
            # the same.
            with open(pushedFile) as pushedF:
                pushedR = json.load(pushedF)
            with open(pulledFile) as pulledF:
                pulledR = json.load(pulledF)

            compareKeys = self.getCompareKeys(rsrcType)

            # If the resource is in the expUnequalRsrcs, then its comparison should
            # fail.
            if pushedR[rt._uniqueKey] in expUnequalUniqueIds:
                self.assertFalse(
                    self.compareRsrcs(
                        pushedR, pulledR, compareKeys))
            else:
                if not self.compareRsrcs(pushedR, pulledR, compareKeys):
                    logging.debug(
                        ("Unexpected mismatched rsrcs:\n"
                         "Pushed:\n{}\nPulled:\n{}\n").format(
                            pushedR, pulledR))
                    self.assertTrue(not "Unexpected mismatched rsrcs")

def unittestMain():
    """ If we need to add wrappers around unittest.main() this function can be
    used for that """

    unittest.main()


allAlerts = TestAlerts.Alert.getTestAlerts()
allDashboards = TestDashboards.Dashboard.getTestDashboards()
