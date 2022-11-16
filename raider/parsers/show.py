import argparse

from raider import Raider
from raider.search import Search
from raider.utils import list_hyfiles, list_projects


def add_show_parser(parser) -> None:
    show_parser = parser.add_parser(
        "show", help="Show projects/hyfiles/flows,etc..."
    )

    show_parser.add_argument(
        "projects", nargs="?", help="Show projects", const=""
    )
    show_parser.add_argument(
        "--hyfiles", nargs="?", help="Show hyfiles", const=""
    )
    show_parser.add_argument(
        "--graphs", nargs="?", help="Show FlowGraphs", const=""
    )
    show_parser.add_argument("--flows", nargs="?", help="Show Flows", const="")
    show_parser.add_argument(
        "--plugins", nargs="?", help="Show Plugins", const=""
    )
    show_parser.add_argument(
        "--inputs", nargs="?", help="Show Input Plugins", const=""
    )
    show_parser.add_argument(
        "--outputs", nargs="?", help="Show Output Plugins", const=""
    )
    show_parser.add_argument(
        "--operations", nargs="?", help="Show Operations", const=""
    )


def run_show_command(args):
    raider = Raider(args.projects)
    matches = Search(raider, args)
    matches.search()
    matches.print()
