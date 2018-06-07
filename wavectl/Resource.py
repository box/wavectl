
import argparse
import json
import abc
import six


class Resource(six.with_metaclass(abc.ABCMeta, object)):
    """A base class that has the common function for wavefront api items,
    building blocks."""

    # Keep a reference to all resources.
    allRsrcs = []

    # A dictionary used as a cache to avoid repeated calculations of format
    # strings in summary tables.
    _summaryTableFormat = {
        True: None,
        False: None,
    }

    @staticmethod
    def _getMaxPrintWidth(rsrcs, key, enableColor):
        """ Accesses all entries in rsrcs and looks at the key in each entry.
        Evaluates the string for each value and returns the longest string
        amongst all values. We use this function for tabular print. Say if we
        want to print all "name" entires of all resources. This function
        returns the necessary max width to allocate"""

        coloringOffset = 0
        # If there is going to be any terminal coloring, allocate some offset
        # for the ansi codes of terminal colors
        if enableColor:
            coloringOffset = 9

        # The [0] addition is to avoid a ValueError: max() arg is an empty sequence
        # error in case no resource can be found.
        width = max([0] + [coloringOffset + len(str(rsrc._state.get(key, "")))
                           for rsrc in rsrcs])

        return width

    @staticmethod
    def _addCustomerTagOption(parser):
        """Adds the --customerTag option to the given parser
        The --customerTag is used by multiple commands so this common function
        can be used to add that command line option"""
        parser.add_argument(
            "--customerTag",
            "-t",
            action="append",
            help="""Narrow down the matching resources by their tags. Multiple
            customer tags can be passed. Resources that contain all tags will
            be returned.""")

    @staticmethod
    def _addMatchOption(parser):
        parser.add_argument("--match", "-m", metavar="REGEX", help="""specify
        a regular expression to further narrow down on matches in any field in
        the resource. If this regex mathes in the resource's representation,
        then the resource will be included in the processing""")

    @classmethod
    def _addSupportedFilterOptions(cls, parser):
        """ Add all command line parameters for regular expression specification
        for individual fields of a resource"""
        clsName = str(cls)
        for l, s in cls._supportedFilters.items():
            parser.add_argument(
                "--" +
                l,
                "-" +
                s,
                metavar="REGEX",
                help="""specify
            a regular expression to further narrow down on matches in the """ +
                l +
                " field in a " +
                clsName)

    @classmethod
    def addSubparser(cls, rsrcsParser):
        """Add resource related command line options to the argparse subparser"""
        clsName = str(cls)
        p = rsrcsParser.add_parser(
            clsName, help="Specify to use {} resources".format(clsName))

        Resource._addCustomerTagOption(p)
        Resource._addMatchOption(p)
        cls._addSupportedFilterOptions(p)

    @classmethod
    def _isColoredKey(cls, key):
        return key in cls._coloredKeys

    @classmethod
    def _summaryTableRowFormat(cls, enableColor):
        """Return the format strings of summary table rows. The summary table
        print uses the format string syntax to have reasonable spacing between
        the columns. Depending on the enableColor option the format strings are
        returned for colored summary table or not"""

        assert enableColor in cls._summaryTableFormat

        cached = cls._summaryTableFormat.get(enableColor)
        if cached:
            return cached

        delimiter = "    "
        fmt = ""
        for stk in cls._summaryTableKeys:
            enCol = enableColor and cls._isColoredKey(stk)
            w = cls._getMaxPrintWidth(cls.allRsrcs, stk, enCol)
            # This is the string format specificatoin
            fmt = fmt + "{" + stk + ":<" + str(w) + "}" + delimiter

        cls._summaryTableFormat[enableColor] = fmt
        return fmt

    @classmethod
    def summaryTableHeader(cls):
        """Return the header of the summary table with correct delimiters"""

        # The header formatting is never colored.
        fmt = cls._summaryTableRowFormat(False)
        h = fmt.format(**{k: k.upper() for k in cls._summaryTableKeys})
        return h

    def __init__(self, state):

        # Make sure all strings can be encoded with ascii. Ignore the unicode
        # characters
        # Without this python2 complains with
        # UnicodeEncodeError: 'ascii' codec can't encode character u'\u2013' in
        # position 24: ordinal not in range(128)
        # Maybe wavefront api server has started to send back unicode characters.
        # TODO: This would be a big performance hit. Attempting to stringify
        # every entry in every resoure.
        for k, v in state.items():
            if isinstance(v, six.string_types):
                try:
                    str(v)
                except UnicodeEncodeError as e:
                    state[k] = v.encode("ascii", "ignore")

        self._state = state

    def doAllRegexesMatch(self, regexes, match):
        # Make sure all regular expressions match in resource state's
        # corresponding key
        rv = all([regex.search(str(self._state.get(key, ""))) is not None
                  for (key, regex) in regexes.items()])

        if not rv:
            # No need to check further
            return False

        if match is None:
            # No other regex to check
            return rv

        # a global match is also specified. That for that regex in the stringified
        # version of the alert
        rv = match.search(json.dumps(self._state))
        return rv is not None

    def jsonStr(self):
        """ Return the json representation of the state in the resource"""
        # Purge the omitted fields
        d = {i: self._state[i]
             for i in self._state if i not in self._omittedFields}

        # The separators avoid the trailing whitespace.
        return json.dumps(d, indent=4, sort_keys=True, separators=(',', ': '))

    def doesContainAllTags(self, tags):
        """Return true if the alert has one of the tags listed in tags set.
        tags: a set of tag strings"""

        if len(tags) == 0:
            # There is no tags to match
            return True

        tagDict = self._state.get("tags")
        if not tagDict:
            # For some reason this alert does not have any tags information.
            return False

        customerTagsList = tagDict.get("customerTags")
        if customerTagsList is None:
            # The Resource does not have any customerTags
            return False

        customerTagsSet = set(customerTagsList)
        # Return true if all given tags exist in the resource.
        return all([(t in customerTagsSet) for t in tags])

    @abc.abstractmethod
    def uniqueId(self):
        raise NotImplementedError

    @abc.abstractmethod
    def browserUrlSuffix(self):
        raise NotImplementedError

    @abc.abstractmethod
    def summaryTableRow(self, enableColor):
        raise NotImplementedError
