from raider import Raider
import argparse

def add_authenticate_parser(parser) -> None:
    auth_parser = parser.add_parser("authenticate", help="Authenticate and exit")
    auth_parser.add_argument("project", nargs="?", help="Project name")
    auth_parser.add_argument("user", nargs="?", help="User to use")
    auth_parser.add_argument(
        "--proxy", help="Send the request through the specified web proxy",
        action="store_true"
    )


def run_authenticate_command(args:argparse.Namespace) -> None:
    raider = Raider(args.project)
    if not args.proxy:
        raider.config.proxy = None

    raider.authenticate(args.user)
