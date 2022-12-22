# Copyright (C) 2020-2022 DigeeX
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
import sys

from raider.config import Config
from raider.flow import Flow
from raider.flowgraph import FlowGraph
from raider.flowstore import FlowStore
from raider.structures import DataStore
from raider.user import Users
from raider.utils import (
    colored_hyfile,
    colored_text,
    create_hy_expression,
    eval_file,
    eval_project_file,
    get_project_file,
    get_project_dir,
    list_hyfiles,
    list_projects,
)


class ProjectConfig(Config):
    def __init__(self, config):
        self.gconfig = config
        self.logger = config.logger
        self.users = None

    @property
    def proxy(self):
        return self.gconfig.proxy

    @property
    def use_proxy(self):
        return self.gconfig.use_proxy

    @property
    def verify(self):
        return self.gconfig.verify

    @property
    def user_agent(self):
        return self.gconfig.user_agent

    @property
    def loglevel(self):
        return self.gconfig.loglevel

    @property
    def active_user(self):
        if self.users:
            username = self.users.active_user
        else:
            self.users = Users()
            username = self.users.active_user

        return self.users[username]


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

    """

    def __init__(self, gconfig, project: str) -> None:
        """Initializes the Project object.

        Sets up the environment necessary to test the specified
        application.

        Args:
          project:
            A string with the name of the application to be
            initialized. If not supplied, the last used application will
            be selected

        """
        self.pconfig = ProjectConfig(gconfig)
        self.name = project
        self.flowstore = FlowStore(self.pconfig)

        self.flows = {}
        self.flowgraphs = {}

        self.logger = gconfig.logger
        self.loaded = False

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
        if self.loaded:
            return

        sys.path.append(get_project_dir(self.name))
        shared_locals: Dict[str, Any]
        shared_locals = {}

        self.logger.debug("Loading hyfiles for %s project", self.name)
        for hyfile in list_hyfiles(self.name):
            self.logger.debug("Loading data from %s", hyfile)
            env_old = shared_locals.copy()
            shared_locals.update(
                eval_project_file(self.name, hyfile, shared_locals)
            )
            env_new = set(shared_locals.keys()) - set(env_old.keys())
            env_new = [item for item in shared_locals if item not in env_old]
            self.flows[hyfile] = []
            self.flowgraphs[hyfile] = []
            for key in env_new:
                if isinstance(shared_locals[key], Flow):
                    self.flows[hyfile].append(key)
                if isinstance(shared_locals[key], FlowGraph):
                    self.flowgraphs[hyfile].append(key)

        for value in shared_locals.values():
            if isinstance(value, Users):
                self.pconfig.users = value

        for key, value in shared_locals.items():
            if isinstance(value, Flow):
                self.flowstore.add_flow(key, value)
            if isinstance(value, FlowGraph):
                self.flowstore.add_flowgraph(key, value)

        if self.flowstore.values:
            first_flow = self.flowstore.values[0]
            first_flow_name = self.flowstore.get_flow_name_by_flow(first_flow)
            for hyfile, flows in self.flows.items():
                if first_flow_name in flows:
                    first_flow_hyfile = hyfile

            self.flowstore.add_flowgraph("DEFAULT", FlowGraph(first_flow))
            self.flowgraphs[first_flow_hyfile].insert(0, "DEFAULT")


        self.loaded = True

        return shared_locals

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
            if self.pconfig.active_user:
                value += create_hy_expression(
                    "_active_user", self.pconfig.active_user.username
                )
            self.logger.debug("Writing to session file %s", filename)
            self.logger.debug("value = %s", str(value))
            proj_file.write(value)

    def print(self, spacing: int = 0) -> None:
        print(" " * spacing + "\x1b[1;30;44m" + self.name + "\x1b[0m")

    def print_hyfile(self, hyfile: str, spacing: int = 0) -> None:
        print(" " * spacing + "- " + colored_hyfile(hyfile))

    def print_flow(self, flow: str, spacing: int = 0) -> None:
        print(" " * spacing + "• " + (flow))

    def print_flowgraph(
        self, flowgraph: str, start: str, test: str = None, spacing: int = 0
    ) -> None:
        if test:
            print(
                " " * spacing
                + "+ "
                + colored_text(flowgraph, "RED-BLACK-B")
                + " -> "
                + colored_text(start, "RESET")
                + " ("
                + colored_text(test, "GREEN-BLACK")
                + ")"
            )
        else:
            print(
                " " * spacing
                + "+ "
                + colored_text(flowgraph, "RED-BLACK-B")
                + " -> "
                + colored_text(start, "RESET")
            )

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
        return {project: {} for project in matches}

    def search_hyfiles(self, results, search: str = None) -> List[str]:
        matches = {}
        for project in results:
            project_hyfiles = sorted(list_hyfiles(project))
            if not search:
                matches.update(
                    {project: {hyfile: {} for hyfile in project_hyfiles}}
                )
            else:
                for hyfile in project_hyfiles:
                    if search.lower() in hyfile.lower():
                        if not project in matches:
                            matches[project] = {}
                        matches[project][hyfile] = {}

        return matches

    def search_flows(
        self,
        results,
        search_flows: str = None,
        search_flowgraphs: str = None,
    ) -> List[str]:
        matches = results
        for project in results.keys():
            hyfiles = results[project]
            for hyfile in hyfiles:
                flows = self[project].flows[hyfile]
                flowgraphs = self[project].flowgraphs[hyfile]
                hyfile_flows = []
                hyfile_flowgraphs = []
                if not search_flows:
                    hyfile_flows = flows
                else:
                    for flow in flows:
                        if search_flows.lower() in flow.lower():
                            hyfile_flows.append(flow)

                if not search_flowgraphs:
                    hyfile_flowgraphs = flowgraphs
                else:
                    for flowgraph in flowgraphs:
                        if search_flowgraphs.lower() in flowgraph.lower():
                            hyfile_flowgraphs.append(flowgraph)

                matches[project][hyfile]["flows"] = hyfile_flows
                matches[project][hyfile]["flowgraphs"] = hyfile_flowgraphs

        return matches
