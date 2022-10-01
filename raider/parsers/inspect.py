import argparse

from raider import Raider


def add_inspect_parser(parser) -> None:
    inspect_parser = parser.add_parser(
        "inspect", help="Inspect Raider configuration"
    )


def run_inspect_command(args):
    raider = Raider()
    print("Configured projects:")
    for item in list_projects():
        print("  - " + item)
        for hyfile in list_hyfiles(item):
            print("    + " + hyfile)
