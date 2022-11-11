import argparse

from raider import Raider


def add_run_parser(parser) -> None:
    run_parser = parser.add_parser("run", help="Run flow or flowgraph")
    run_parser.add_argument("project", nargs="?", help="Project name")
    run_parser.add_argument("--flow", help="Run a single Flow")
    run_parser.add_argument(
        "--graph",
        nargs="?",
        const="DEFAULT",
        default="DEFAULT",
        help="Run a series of Flows in the FlowGraph until no Next Operation is found",
    )
    run_parser.add_argument(
        "--proxy",
        help="Send the request through the specified web proxy.",
        action="store_true",
    )


def run_run_command(args: argparse.Namespace) -> None:
    raider = Raider(args.project)
    if args.proxy:
        raider.config.use_proxy = True

    if args.flow:
        raider.run_flow(args.flow)
    else:
        raider.run_flowgraph(args.graph)
