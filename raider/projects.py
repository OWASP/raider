# Copyright (C) 2022 DigeeX
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Project classes holding project configuration.
"""

from typing import Dict, List, Optional

import igraph

from raider.authentication import Authentication
from raider.config import Config
from raider.flow import AuthFlow, Flow
from raider.functions import Functions
from raider.structures import DataStore, FlowGraph
from raider.user import Users
from raider.utils import (
    colored_hyfile,
    create_hy_expression,
    eval_file,
    eval_project_file,
    get_project_file,
    list_hyfiles,
    list_projects,
)


class Project:
    """Class holding all the project related data.

    This class isn't supposed to be used directly by the user, instead
    the Raider class should be used, which will deal with the
    Project class internally.

    Attributes:
      name:
        A string with the name of the application.
      base_url:
        A string with the base URL of the application.
      config:
        A Config object with Raider global configuration plus the
        variables defined in hy configuration files related to the
        Project.
      users:
        A UserStore object generated from the "_users" variable set in
        the hy configuration files for the project.
      active_user:
        A User object pointing to the active user inside the "users"
        object.
      authentication:
        An Authentication object containing all the Flows relevant to
        the authentication process. It's created out of the
        "_authentication" variable from the hy configuration files.
      functions:
        A Functions object with all Flows that don't affect the
        authentication process. This object is being created out of the
        "_functions" variable from the hy configuration files.

    """

    def __init__(self, config, project: str) -> None:
        """Initializes the Project object.

        Sets up the environment necessary to test the specified
        application.

        Args:
          project:
            A string with the name of the application to be
            initialized. If not supplied, the last used application will
            be selected

        """
        self.config = config
        self.name = project
        self.flows = None
        self.logger = config.logger

    def load(self):
        """Loads project settings.

        Goes through all the ".hy" files in the project directory,
        evaluates them all, and returns the created locals, making them
        available to the rest of Raider.

        Files are loaded in alphabetical order, and objects created in
        one of them will be available to the next one, eliminating the
        need to use imports. This allows the user to split the
        configuration files however it makes sense, and Raider doesn't
        impose any restrictions on those files.

        All ".hy" files in the project directory are evaluated, which
        could be considered unsafe and could cause all kinds of security
        issues, but Raider assumes the user knows what they're doing and
        will not copy/paste hylang code from untrusted sources.

        Returns:
          A dictionary as returned by the locals() function. It contains
          all of the locally defined objects in the ".hy" configuration
          files.
        """
        shared_locals: Dict[str, Any]
        shared_locals = {}

        flows = {}
        auth_graph = FlowGraph()
        func_graph = FlowGraph()

        self.logger.debug(
            "Loading data from hyfiles for %s project", self.name
        )
        for hyfile in list_hyfiles(self.name):
            self.logger.debug("Loading data from %s", hyfile)
            env_old = shared_locals.copy()
            shared_locals.update(
                eval_project_file(self.name, hyfile, shared_locals)
            )
            env_new = set(shared_locals.keys()) - set(env_old.keys())
            flows[hyfile] = []
            for key in env_new:
                if isinstance(shared_locals[key], Flow):
                    flows[hyfile].append(key)

        for value in shared_locals.values():
            if isinstance(value, Users):
                self.users = value

        active_user = self.users.active_user
        if active_user and active_user in self.users:
            self.active_user = self.users[active_user]
        else:
            self.active_user = self.users.active

        for key, value in shared_locals.items():
            if isinstance(value, AuthFlow):
                auth_graph.add_flow(key, value)
            elif isinstance(value, Flow):
                func_graph.add_flow(key, value)

        self.authentication = Authentication(self.config, auth_graph)
        self.functions = Functions(self.config, func_graph)
        self.flows = flows

        return shared_locals

    def authenticate(self, username: str = None) -> None:
        """Authenticates the user.

        Runs all the steps of the authentication process defined in the
        hy config files for the application.

        Args:
          username:
            A string with the user to be authenticated. If not supplied,
            the last used username will be selected.

        """
        self.load()
        if username:
            self.active_user = self.users[username]
        self.authentication.run_all(self.active_user, self.config)
        self.write_project_file()

    def auth_step(self) -> None:
        """Runs next authentication step.

        Runs one the steps of the authentication process defined in the
        hy config files for the application.

        Args:
          username:
            A string with the user to be authenticated. If not supplied,
            the last used username will be selected.

        """
        self.authentication.run_current_stage(self.active_user, self.config)
        self.write_project_file()

    def write_session_file(self) -> None:
        """Saves session data.

        Saves user related session data in a file for later use. This
        includes cookies, headers, and other data extracted using
        Plugins.

        """
        filename = get_project_file(self.name, "_userdata.hy")
        value = ""
        cookies = {}
        headers = {}
        data = {}
        with open(filename, "w", encoding="utf-8") as sess_file:
            for username in self.users:
                user = self.users[username]
                cookies.update({username: user.cookies.to_dict()})
                headers.update({username: user.headers.to_dict()})
                data.update({username: user.data.to_dict()})

            value += create_hy_expression("_cookies", cookies)
            value += create_hy_expression("_headers", headers)
            value += create_hy_expression("_data", data)
            self.logger.debug("Writing to session file %s", filename)
            self.logger.debug("value = %s", str(value))
            sess_file.write(value)

    def load_session_file(self) -> None:
        """Loads session data.

        If session data was saved with write_session_file() this
        function will load this data into existing :class:`User
        <raider.user.User>` objects.

        """
        filename = get_project_file(self.name, "_userdata.hy")
        output = eval_file(filename)
        cookies = output.get("_cookies")
        headers = output.get("_headers")
        data = output.get("_data")

        if cookies:
            for username in cookies:
                self.users[username].set_cookies_from_dict(cookies[username])

        if headers:
            for username in headers:
                self.users[username].set_headers_from_dict(headers[username])

        if data:
            for username in data:
                self.users[username].set_data_from_dict(data[username])

    def write_project_file(self) -> None:
        """Writes the project settings.

        For now only the active user is saved, so that the next time the
        project is used, there's no need to specify the user manually.

        """
        filename = get_project_file(self.name, "_project.hy")
        value = ""
        with open(filename, "w", encoding="utf-8") as proj_file:
            value += create_hy_expression(
                "_active_user", self.active_user.username
            )
            self.logger.debug("Writing to session file %s", filename)
            self.logger.debug("value = %s", str(value))
            proj_file.write(value)

    def print(self, spacing: int = 0) -> None:
        print(" " * spacing + "\x1b[1;30;44m" + self.name + "\x1b[0m")

    def print_hyfiles(
        self, matches: List[str] = None, spacing: int = 0
    ) -> None:
        for hyfile in self.hyfiles:
            if not matches or hyfile in matches:
                print(" " * spacing + "- " + colored_hyfile(hyfile))

    def print_flows(
        self, hyfile: str, matches: List[str] = None, spacing: int = 0
    ) -> None:
        for flow in self.flows[hyfile]:
            if not matches or flow in matches:
                print(" " * spacing + "• " + (flow))

    @property
    def hyfiles(self):
        return sorted(list_hyfiles(self.name))


class Projects(DataStore):
    """Class storing Raider projects.

    This class inherits from DataStore, and converts the values into
    Project objects.

    """

    def __init__(self, config: Config, active_project: str = None) -> None:
        """Initializes a Projects object.

        Given a list of Project objects, create the Projects DataStore
        containing them.

        Args:
          projects:
            A list of Project objects to be added to the Projects
            DataStore.

        """
        if active_project:
            config.active_project = active_project

        values = {}
        if list_projects():
            for project in list_projects():
                values[project] = Project(config, project)

        super().__init__(values)

    def search_projects(self, search: str = None) -> List[str]:
        matches = set()
        if not search:
            matches = sorted(self.keys())
            return matches

        for project in self.values():
            if search.lower() in project.name.lower():
                matches.add(project.name)

        matches = sorted(list(matches))
        return matches

    def search_hyfiles(
        self, projects: List[str], search: str = None
    ) -> List[str]:
        matches = {}
        for project in projects:
            project_hyfiles = sorted(list_hyfiles(project))
            if not search:
                matches.update({project: project_hyfiles})
            else:
                matches[project] = []
                for hyfile in project_hyfiles:
                    if search.lower() in hyfile.lower():
                        matches[project].append(hyfile)

        return matches

    def search_flows(
        self, hyfiles: Dict[str, List[str]], search: str = None
    ) -> List[str]:
        matches = {}
        for project in hyfiles.keys():
            for hyfile in hyfiles[project]:
                if not search:
                    matches[project] = {}
                    matches[project][hyfile] = []
                    matches[project][hyfile].append(
                        self[project].flows[hyfile]
                    )
                else:
                    for flow in self[project].flows[hyfile]:
                        if search.lower() in flow.lower():
                            matches[project] = {}
                            matches[project][hyfile] = []
                            matches[project][hyfile].append(flow)

        return matches
