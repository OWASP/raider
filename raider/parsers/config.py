from raider import Raider
import argparse

def add_config_parser(parser) -> None:
    config_parser = parser.add_parser(
        "config", help="Configure raider"
    )
    config_parser.add_argument(
        "--proxy", help="Set the web proxy",
    )
    config_parser.add_argument(
        "--verify", help="Verify SSL requests",
    )
    config_parser.add_argument(
        "--loglevel", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)",
    )
    config_parser.add_argument(
        "--user-agent", help="User agent to use with Raider",
    )
    config_parser.add_argument(
        "--active_project", help="Set active project (By default last used project)",
    )

def run_config_command(args):
    raider = Raider()
    if args.proxy:
        raider.config.proxy = args.proxy
    if args.verify:
        raider.config.verify = args.verify
    if args.loglevel:
        raider.config.loglevel = args.loglevel
    if args.user_agent:
        raider.config.user_agent = args.user_agent
    if args.active_project:
        raider.config.active_project = args.active_project
    
    raider.config.write_config_file()
    raider.config.print_config()
    
