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
from raider.utils import list_projects


def main() -> None:
    """Parses command line interface arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--proxy", help="Send the request through the specified web proxy"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose mode"
    )
    parser.add_argument("--user", help="Set up the active user")

    subparsers = parser.add_subparsers(help="Command", dest="command")

    shell_parser = subparsers.add_parser(
        "shell", help="Run commands in an interactive shell"
    )
    auth_parser = subparsers.add_parser(
        "authenticate", help="Authenticate and exit"
    )
    func_parser = subparsers.add_parser(
        "run",
        help="Authenticate, run function (or chain of functions) and exit",
    )
    subparsers.add_parser("ls", help="List configured projects")

    shell_parser.add_argument("project", help="Project name")
    auth_parser.add_argument("project", help="Project name")
    func_parser.add_argument("project", help="Project name")

    func_parser.add_argument("function", help="Function name to run")
    func_parser.add_argument(
        "--chain", help="Run subsequent chained functions", action="store_true"
    )

    args = parser.parse_args()

    if args.command in ["shell", "authenticate", "run"]:
        raider = Raider(args.project)
        if args.proxy:
            raider.config.proxy = args.proxy
        else:
            raider.config.proxy = None

        if args.user:
            raider.authenticate(args.user)
        else:
            raider.authenticate()

        if args.command == "run":
            if args.chain:
                raider.run_chain(args.function)
            else:
                raider.run_function(args.function)

        if args.command == "shell":
            embed(colors="neutral")

    elif args.command == "ls":
        print("Configured projects")
        for item in list_projects():
            print("  - " + item)


if __name__ == "__main__":
    main()
