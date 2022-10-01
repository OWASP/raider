import argparse

from raider import Raider
from raider.search import Search
from raider.utils import list_hyfiles, list_projects


def add_edit_parser(parser) -> None:
    edit_parser = parser.add_parser("edit", help="Edit projects and hyfiles")

    edit_parser.add_argument(
        "--projects", nargs="?", help="Edit projects", const=""
    )
    edit_parser.add_argument(
        "--hyfiles", nargs="?", help="Edit hyfiles", const=""
    )


def run_edit_command(args):
    raider = Raider(args.projects)
    matches = Search(raider, args)
    matches.search()
    if matches.print_flows_enabled:
        matches.print_flows()
    elif matches.print_hyfiles_enabled:
        matches.print_hyfiles()
    elif matches.print_projects_enabled:
        matches.print_projects()
    else:
        args.projects = ""
        args.hyfiles = ""
        matches.print_hyfiles()
