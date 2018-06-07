

from __future__ import absolute_import
from __future__ import print_function

import os
import json

from .BaseCommand import BaseCommand
from builtins import input


class ConfigCommand(BaseCommand):
    """ A class implementing the `config .....` command. It is mainly used
    for saving the host name, api key and the default tag."""

    def handleCmd(self, args):
        """Ask for some input from the user. Get the wavefront host uri, the
        api key to use and the default tags if the user wants to narrow down
        her requests with some tags by default"""

        h = input("Wavefront host url: ")
        token = input("Api token: ")

        self.config = {
            self.wavefrontHostKey: h,
            self.apiTokenKey: token,
        }

        s = json.dumps(
            self.config,
            sort_keys=True,
            indent=4,
            separators=(
                ',',
                ': '))

        BaseCommand.makeDirsIgnoreExisting(self.configDirPath)

        fn = os.path.join(self.configDirPath, self.configFileName)
        print(
            "Writing the following config to the config file at {0}: \n{1}".format(
                fn,
                s))
        with open(fn, "w") as f:
            f.write(s)

    def addCmd(self, subParsers):
        p = subParsers.add_parser(
            "config", help="Set wavefront host, api token.")
        p.set_defaults(wavefrontConfigFuncToCall=self.handleCmd)

    def __init__(self, *args, **kwargs):
        super(ConfigCommand, self).__init__(*args, **kwargs)
