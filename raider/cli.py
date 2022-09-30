# Copyright (C) 2022 DigeeX
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

from raider.raider import Raider
from raider.utils import list_projects, list_hyfiles
from raider.parsers.show import add_show_parser, run_show_command
from raider.parsers.shell import add_shell_parser, run_shell_command
from raider.parsers.config import add_config_parser, run_config_command
from raider.parsers.authenticate import add_authenticate_parser, run_authenticate_command
from raider.parsers.run_flow import add_run_flow_parser, run_run_flow_command
from raider.parsers.run_graph import add_run_graph_parser, run_run_graph_command
from raider.parsers.inspect import add_inspect_parser, run_inspect_command


def main() -> None:
    """Parses command line interface arguments."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Command", dest="command")

    commands = {
        "show": run_show_command,
        "shell": run_shell_command,
        "config": run_config_command,
        "authenticate": run_authenticate_command,
        "run_flow": run_run_flow_command,
        "run_graph": run_run_graph_command,
        "inspect": run_inspect_command,
    }

    add_show_parser(subparsers)
    add_authenticate_parser(subparsers)
    add_config_parser(subparsers)
    add_inspect_parser(subparsers)
    add_run_flow_parser(subparsers)
    add_run_graph_parser(subparsers)
    add_shell_parser(subparsers)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
    else:
        commands[args.command](args)

if __name__ == "__main__":
    main()
