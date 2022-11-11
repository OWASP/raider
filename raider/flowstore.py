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


import sys
from typing import Any, Dict, List, Optional, Union

import igraph

import raider.plugins as Plugins
from raider.config import Config
from raider.flow import Flow
from raider.user import User


class FlowStore:
    def __init__(self, config) -> None:
        self.flows = igraph.Graph(directed=True)
        self.flowgraphs = {}
        self.config = config
        self.logger = config.logger

    def add_flow(self, key: str, value: str) -> None:
        self.flows.add_vertices(1)
        index = self.flows.vcount() - 1
        self.flows.vs[index]["name"] = key
        self.flows.vs[index]["object"] = value

    def add_flowgraph(self, key: str, value: str) -> None:
        self.flowgraphs[key] = value

    def __getitem__(self, name: Any) -> Any:
        """Getter to return a Flow by the name."""
        if name in self.keys:
            flow_id = self.get_flow_id_by_name(name)
            return self.flows.vs[flow_id]["object"]
        return None

    def get_flow_id_by_name(self, flow_name: str) -> int:
        return self.keys.index(flow_name)

    def get_flow_id_by_flow(self, flow: Flow) -> int:
        return self.values.index(flow)

    def get_flow_name_by_flow(self, flow: Flow) -> int:
        return self.get_flow_name_by_id(self.get_flow_id_by_flow(flow))

    def get_flow_name_by_id(self, flow_id: int) -> str:
        """Returns the flow name given its number.

        Each authentication step is given an index based on its position
        in the "_authentication" list. This function returns the name of
        the Flow based on its position in this list.

        Args:
          flow_id:
            An integer with the index of the flow.

        Returns:
          A string with the name of the Flow in the position "flow_id".

        """
        if not self.flows.vs:
            return None
        return self.flows.vs[flow_id]["name"]

    def get_flow_index(self, name: str) -> int:
        """Returns the index of the flow given its name.


        Returns:
          An integer with the index of the Flow with the specified "name".
        """
        if isinstance(name, bool):
            return None
        return self.flows.vs[::]["name"].index(name)

    @property
    def keys(self) -> List[str]:
        if not self.flows.vs:
            return []
        return self.flows.vs[::]["name"]

    @property
    def values(self) -> List[Any]:
        if not self.flows.vs:
            return []
        return self.flows.vs[::]["object"]

    def run_flow(
        self, config: Config, flow_id: Union[int, str]
    ) -> Optional[str]:
        """Runs one authentication Flow.

        First, the Flow object of the specified flow is identified,
        then the related HTTP request is processed, sent, the response
        is received, and the operations are run on the Flow.

        Args:
          flow_id:
            A string or an integer identifying the authentication flow
            to run. If it's a string, it's the name of the Flow, and if
            it's an integer, it's the index of the Flow object in the
            "_authentication" variable.
          user:
            A User object containing the credentials and where the user
            specific data will be stored.
          config:
            A Config object with the global Raider settings.

        Returns:
          Optionally, this function returns a string with the name of
          the next Flow in the authentication process.

        """

        flow: Optional[Flow]
        if isinstance(flow_id, int):
            flow_name = self.get_flow_name_by_id(flow_id)
            flow = self[flow_name]
        elif isinstance(flow_id, str):
            flow = self[flow_id]

        if not flow:
            self.logger.critical(
                "Flow %s not defined. Cannot continue", flow_id
            )
            sys.exit()

        flow.execute(config)

        if flow.outputs:
            for item in flow.outputs:
                if isinstance(item, Plugins.Cookie):
                    config.active_user.set_cookie(item)
                elif isinstance(item, Plugins.Header):
                    config.active_user.set_header(item)
                elif isinstance(
                    item, (Plugins.Regex, Plugins.Html, Plugins.Json)
                ):
                    config.active_user.set_data(item)

        operations_result = flow.run_operations()
        if isinstance(operations_result, str):
            return operations_result
        else:
            return None

    def run_chain(self, config: Config, flowgraph: str) -> None:
        """Runs all authentication flows.

        This function will run all authentication flows for the
        specified User and will take into account the supplied Config
        for things like the user agent and the web proxy to use.

        Args:
          user:
            A User object containing the credentials and where the user
            specific data will be stored.
          config:
            A Config object with the global Raider settings.

        """

        flow = self.flowgraphs[flowgraph].start
        flow_id = self.get_flow_id_by_flow(flow)
        next_flow = self.run_flow(config, flow_id)
        while next_flow:
            next_flow = self.run_flow(config, next_flow)
