import argparse

from raider import Raider


def add_run_flow_parser(parser) -> None:
    run_flow_parser = parser.add_parser("run_flow", help="Run a single Flow")
    run_flow_parser.add_argument("project", help="Project name")
    run_flow_parser.add_argument("flow", help="Flow name to run")


def run_run_flow_command(args):
    raider = Raider(args.project)
    if not args.proxy:
        raider.config.proxy = None

    if args.user:
        raider.authenticate(args.user)
    else:
        raider.authenticate()

    raider.run_function(args.function)
