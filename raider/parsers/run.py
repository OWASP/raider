import argparse
import sys

from raider import Raider
from raider.utils import list_projects


def add_run_parser(parser) -> None:
    run_parser = parser.add_parser("run", help="Run Flow or Flowgraph")
    run_parser.add_argument("project", nargs="?", help="Project name")
    run_parser.add_argument(
        "flows",
        nargs="?",
        const="DEFAULT",
        default="DEFAULT",
        help="Run a series of Flows/FlowGraphs",
    )
    run_parser.add_argument(
        "--proxy",
        help="Send the request through the specified web proxy.",
        action="store_true",
    )
    run_parser.add_argument(
        "--test",
        help="Run the FlowGraph's test Flow.",
        action="store_true",
    )


def run_run_command(args: argparse.Namespace) -> None:
    raider = Raider(args.project)
    if args.proxy:
        raider.gconfig.use_proxy = True

    if not list_projects():
        raider.logger.critical(
            "No application have been configured. Cannot run!"
        )
        sys.exit()

    if raider.project:
        raider.project.load()
    else:
        raider.logger.critical(args.project + " doesn't exist. Cannot run!")
        sys.exit()

    raider.run(args.flows, args.test)

    raider.project.write_project_file()
