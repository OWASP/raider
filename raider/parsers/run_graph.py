import argparse

from raider import Raider


def add_run_graph_parser(parser) -> None:
    run_graph_parser = parser.add_parser(
        "run_graph",
        help="Run a series of flows in the graph until no NextStage is found.",
    )
    run_graph_parser.add_argument("project", help="Project name")
    run_graph_parser.add_argument("flow", help="Flow name to run")


def run_run_graph_command(args):
    raider = Raider(args.project)
    if not args.proxy:
        raider.config.proxy = None

    if args.user:
        raider.authenticate(args.user)
    else:
        raider.authenticate()

    raider.run_chain(args.function)
