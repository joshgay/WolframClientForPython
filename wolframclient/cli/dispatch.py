# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from wolframclient.cli.utils import discover_with_convention, SimpleCommand
from wolframclient.utils.importutils import import_string

import sys

class DispatchCommand(SimpleCommand):

    modules = ['wolframclient.cli.commands']
    class_name = 'Command'

    def subcommands(self):
        return discover_with_convention(self.modules, self.class_name)

    def handle(self, attr = None):
        all_commands = self.subcommands()

        if attr in all_commands:
            return import_string(all_commands[attr])(self.subcommand_args(), name = all_commands[attr]).main()

        self.print('Select one of the following commands:')
        for command in sorted(all_commands.keys()):
            self.print(' -', command)

        sys.exit(1)

    def subcommand_args(self):
        argv = list(self.argv)
        if len(argv) > 1:
            argv.pop(1)
        return argv

    def main(self):
        if len(self.argv) > 1 and self.argv[1]:
            return self.handle(self.argv[1])
        return self.handle()

def execute_from_command_line(argv = None, **opts):
    return DispatchCommand(argv).main()