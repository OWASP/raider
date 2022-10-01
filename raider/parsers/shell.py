import argparse

from raider import Raider


def add_shell_parser(parser) -> None:
    shell_parser = parser.add_parser(
        "shell", help="Run commands in an interactive shell"
    )
    shell_parser.add_argument("project", help="Project name")


def run_shell_command(args):
    raider = Raider(args.project)
    embed(colors="neutral")
