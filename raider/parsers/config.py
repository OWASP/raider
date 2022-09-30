from raider import Raider
import argparse

def add_config_parser(parser) -> None:
    config_parser = parser.add_parser(
        "config", help="Configure raider"
    )
    config_parser.add_argument(
        "--proxy", help="Set the web proxy",
    )


def run_config_command(args):
    raider = Raider()
    print("Configured projects:")
    if args.proxy:
        raider.config.proxy = args.proxy
    raider.config.write_config_file()
    print("Raider config:")
    print(raider.config.proxy)
