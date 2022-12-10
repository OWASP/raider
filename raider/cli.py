# Copyright (C) 2020-2022 DigeeX
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Raider command line interface.
"""

import argparse

from IPython import embed

from raider.parsers.config import add_config_parser, run_config_command
from raider.parsers.delete import add_delete_parser, run_delete_command
from raider.parsers.edit import add_edit_parser, run_edit_command
from raider.parsers.inspect import add_inspect_parser, run_inspect_command
from raider.parsers.new import add_new_parser, run_new_command
from raider.parsers.run import add_run_parser, run_run_command
from raider.parsers.shell import add_shell_parser, run_shell_command
from raider.parsers.show import add_show_parser, run_show_command
from raider.raider import Raider
from raider.utils import list_hyfiles, list_projects


def main() -> None:
    """Parses command line interface arguments."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Command", dest="command")

    commands = {
        "show": run_show_command,
        "config": run_config_command,
        "new": run_new_command,
        "delete": run_delete_command,
        "edit": run_edit_command,
        "shell": run_shell_command,
        "run": run_run_command,
        "inspect": run_inspect_command,
    }

    add_show_parser(subparsers)
    add_config_parser(subparsers)
    add_new_parser(subparsers)
    add_delete_parser(subparsers)
    add_edit_parser(subparsers)
    add_inspect_parser(subparsers)
    add_run_parser(subparsers)
    add_shell_parser(subparsers)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
    else:
        commands[args.command](args)


if __name__ == "__main__":
    main()
