import argparse
import os
import shutil

from raider import Raider
from raider.search import Search
from raider.utils import colored_text, get_project_dir


def add_delete_parser(parser) -> None:
    delete_parser = parser.add_parser(
        "delete", help="Delete projects and hyfiles"
    )

    delete_parser.add_argument("project", help="Project name to delete")
    delete_parser.add_argument(
        "hyfiles", nargs="?", help="Delete hyfiles matching this argument"
    )


def run_delete_command(args):
    raider = Raider()
    logger = raider.logger
    project_dir = get_project_dir(args.project)
    if os.path.isdir(project_dir):
        if os.listdir(project_dir):
            raider.logger.warning(
                'Project "%s" contains hyfiles at %s.',
                args.project,
                project_dir,
            )
            answer = input(
                colored_text(
                    "Are you sure you want to delete it? (Y/N) ", "RED-BLACK-B"
                )
            )
            if answer[0].upper() == "Y":
                raider.logger.warning(
                    "Deleting %s with all hyfiles inside.", project_dir
                )
                shutil.rmtree(project_dir)
        else:
            raider.logger.warning("Deleting %s.", project_dir)
            os.rmdir(project_dir)
    else:
        raider.logger.warning("Directory %s doesn't exist.", args.project)
