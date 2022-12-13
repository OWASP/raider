import argparse
import os

from raider import Raider
from raider.search import Search
from raider.utils import get_project_dir, list_hyfiles, list_projects


def add_edit_parser(parser) -> None:
    edit_parser = parser.add_parser("edit", help="Edit projects and hyfiles")

    edit_parser.add_argument("project", help="Project name")
    edit_parser.add_argument("hyfile", help="hyfile name to edit")


def run_edit_command(args):
    raider = Raider(args.project)
    project_dir = get_project_dir(args.project)
    filepath = os.path.join(project_dir, args.hyfile)
    editor = os.getenv("EDITOR") or "vim"
    if not os.path.isfile(filepath):
        raider.logger.warning(
            "File " + filepath + " doesn't exist. Creating new."
        )

    os.system("%s %s" % (editor, filepath))
