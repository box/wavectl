
from __future__ import absolute_import
from __future__ import print_function
import json
import os
import threading
import errno


class ConfigError(Exception):
    pass


class BaseCommand(object):
    """ A base class for all commands in wavectl"""

    # A global lock used for critical section protection

    _lock = threading.Lock()

    class LockAnchor(object):
        """ And Anchor type (RAII pattern) that acquires a lock at the
        context creation time and releases it at the exit time"""

        def __init__(self):
            pass

        def __enter__(self):
            BaseCommand._lock.acquire()

        def __exit__(self, type, value, traceback):
            BaseCommand._lock.release()

    # The directory and name of the config file. By default the config file is
    # located at ~/.wavectl/config.
    configDirPath = os.path.expanduser("~/.wavectl")
    configFileName = "config"

    # The key names used in the config dictionary.
    wavefrontHostKey = "wavefrontHost"
    apiTokenKey = "apiToken"

    wavefrontHostOptionName = "--" + wavefrontHostKey
    apiTokenOptionName = "--" + apiTokenKey

    @staticmethod
    def makeDirsIgnoreExisting(p):
        """unix mkdir -p functionality. Creates the directory given in the path
        p. Also creates the intermediate directories. Does not complain if the
        root directory exists already."""
        try:
            os.makedirs(p)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(p):
                pass
            else:
                raise

    def _checkConfig(self):
        """Verify that the final compiled config has all the compulsory fields
        speficied. A config must have a wavefrontHost and an apiToken raise
        an exception if none of them exist"""

        if self.config.get(self.wavefrontHostKey) is None:
            raise ConfigError(
                ("The wavefront host url is not known. Either execute "
                 "`wavectl config ...` or pass {0} command line option").format(
                    self.wavefrontHostOptionName))
        if self.config.get(self.apiTokenKey) is None:
            raise ConfigError(
                ("The wavefront api token is not known. Either execute "
                 "`wavectl config ...` or pass {0} command line option").format(
                    self.apiTokenOptionName))

    def _getConfig(self):
        """ Read the config file (if exists) and use the command line flags to
        populate the self.config if it is not known already. If the required
        information is not known, raise an exception."""

        # This function may be called from multiple threads at once.
        # So make sure only one instance is running at a time
        # This function modifies state in the
        with BaseCommand.LockAnchor():
            if self.config is not None:
                # Config file has been read already
                return

            newConfig = {}
            fp = os.path.join(self.configDirPath, self.configFileName)
            if os.path.isfile(fp):
                with open(fp) as f:
                    newConfig = json.load(f)

            newConfig.update(self.configFromCommandLine)

            self.config = newConfig

            self._checkConfig()

    def handleCmd(self, args):
        """ Extact the relevant commands from the command line and save in
        static variables. They will be used and evaluated later"""
        if args.wavefrontHost:
            self.configFromCommandLine[self.wavefrontHostKey] = args.wavefrontHost
        if args.apiToken:
            self.configFromCommandLine[self.apiTokenKey] = args.apiToken

    def addCmd(self, parser):
        """ Adds the command line parameters for specifying the wavefront host
        and the apiToken from the command line. The options from the command line
        take precedence over the ones in the config file"""

        parser.add_argument(
            self.wavefrontHostOptionName,
            help="""Speficy the url of the wavefront host. If specified, this
            takes precedence over the config file entry.""")
        parser.add_argument(
            self.apiTokenOptionName,
            help="""Speficy the api token to use while communicating with the
            wavefront host. If specified, this takes precedence over the config
            file entry.""")

    def __init__(self, designForTestConfigDir=None):
        # The config for the wavectl command. Either read from the
        # config file on demand or set by the user with `wavectl config`
        # command

        if designForTestConfigDir:
            # Design for testability. We may want to change the
            # config dir location to have better test visibility.
            self.configDirPath = designForTestConfigDir

        self.config = None
        # The config values if speficied from the command line.
        self.configFromCommandLine = {}
