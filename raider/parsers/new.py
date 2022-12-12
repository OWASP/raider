import argparse
import os

from raider import Raider
from raider.search import Search
from raider.utils import colored_text, get_project_dir


def add_new_parser(parser) -> None:
    new_parser = parser.add_parser(
        "new", help="Create new projects and hyfiles"
    )

    new_parser.add_argument(
        "project", help="Project name (will be created if doesn't exist)"
    )
    new_parser.add_argument(
        "hyfile", nargs="?", help="Add new hyfile to the project"
    )


def run_new_command(args):
    raider = Raider()
    project_dir = get_project_dir(args.project)
    if os.path.isdir(project_dir):
        raider.logger.info(
            'Project "%s" already exists, not creating new directory.',
            args.project,
        )
    else:
        os.makedirs(project_dir)
        raider.logger.info(
            'Created new project "%s" located at %s.',
            args.project,
            project_dir,
        )

    if args.hyfile:
        filepath = os.path.join(project_dir, args.hyfile)
    else:
        filename = input(
            colored_text(
                "New file name (recommended in XX_name.hy format where XX=digits): ",
                "BLUE-BLACK-B",
            )
        )
        filepath = os.path.join(project_dir, filename)
    if os.path.isfile(filepath):
        raider.logger.warning("File %s already exists.", filepath)
        answer = input(
            colored_text(
                "Are you sure you want to overwrite it? (Y/N) ", "RED-BLACK-B"
            )
        )
        if answer[0].upper() == "Y":
            raider.logger.info("Overwriting file %s.", filepath)
            open(filepath, "w").close()
    else:
        raider.logger.info("Creating file %s.", filepath)
        open(filepath, "w").close()

    editor = os.getenv("EDITOR") or "vim"
    os.system("%s %s" % (editor, filepath))
