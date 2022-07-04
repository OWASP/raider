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

"""Flow class holding the information exchanged between server and client.
"""

from typing import List, Optional

import requests

from raider.config import Config
from raider.operations import Operation
from raider.plugins.common import Plugin
from raider.request import Request
from raider.user import User


class Flow:
    """Class dealing with the information exchange from HTTP communication.

    A Flow object in Raider defines all the information about one
    single HTTP information exchange. It contains one ``request``, the
    ``response``, the ``outputs`` that needs to be extracted from the
    response, and a list of ``operations`` to be run when the exchange
    is over.

    Use this only when working with requests that *DON't* change the
    authentication state.  It's used in the :class:`Functions
    <raider.functions.Functions>` class to run arbitrary actions when
    it doesn't affect the authentication state.

    When the authentication state changes, use :class:`AuthFlow
    <raider.flow.AuthFlow>` objects.

    Attributes:
      request:
        A :class:`Request <raider.request.Request>` object detailing the
        HTTP request with its elements.
      response:
        A :class:`requests.model.Response` object. It's empty until the
        request is sent. When the HTTP response arrives, it's stored
        here.
      outputs:
        A list of :class:`Plugin <raider.plugins.Plugin>` objects
        detailing the pieces of information to be extracted from the
        response. Those will be later available for other Flow objects.
      operations:
        A list of :class:`Operation <raider.operations.Operation>`
        objects to be executed after the response is received and
        outputs are extracted. Should contain a :class:`NextStage
        <raider.operations.NextStage>` operation if another Flow is
        expected.
    """

    def __init__(
        self,
        request: Request,
        outputs: Optional[List[Plugin]] = None,
        operations: Optional[List[Operation]] = None,
    ) -> None:
        """Initializes the Flow object.

        Creates the Flow object with the associated Request, the outputs
        to be extracted, and the operations to be run upon completion.

        Args:
          request:
            A Request object associated with this Flow.
          outputs:
            A list of Plugins to be used for extracting data from the
            response.
          operations:
            A list of Operations to be run after the response is
            received.

        """
        self.outputs = outputs
        self.operations = operations

        self.request = request
        self.response: Optional[requests.models.Response] = None

    def execute(self, user: User, config: Config) -> None:
        """Sends the request and extracts the outputs.

        Given the user in context and the global Raider configuration,
        sends the HTTP request and extracts the defined outputs.

        Iterates through the defined outputs in the Flow object, and
        extracts the data from the HTTP response, saving it in the
        respective :class:`Plugin <raider.plugins.Plugin>` object.

        Args:
          user:
            An object containing all the user specific data relevant for
            this action.
          config:
            The global Raider configuration.

        """
        self.response = self.request.send(user, config)
        if self.outputs:
            for output in self.outputs:
                if output.needs_response:
                    output.extract_value_from_response(self.response)
                    if output.name_not_known_in_advance:
                        output.extract_name_from_response(self.response)
                elif output.depends_on_other_plugins:
                    for item in output.plugins:
                        item.get_value(user.to_dict())
                    output.get_value(user.to_dict())

    def get_plugin_values(self, user: User) -> None:
        """Given a user, get the plugins' values from it.

        Args:
          user:
            A :class:`User <raider.user.User>` object with the userdata.

        """
        flow_inputs = self.request.list_inputs()
        if flow_inputs:
            for plugin in flow_inputs.values():
                plugin.get_value(user.to_dict())

    def run_operations(self) -> Optional[str]:
        """Runs the defined :class:`operations <raider.operations.Operation>`.

        Iterates through the defined ``operations`` and executes them
        one by one. Iteration stops when the first :class:`NextStage
        <raider.operations.NextStage>` operations is encountered.

        Returns:
          A string with the name of the next stage to run or None.

        """
        next_stage = None

        if self.operations:
            for item in self.operations:
                next_stage = item.run(self.response)
                if next_stage:
                    break

        return next_stage


class AuthFlow(Flow):
    """Class dealing with the authentication Flows.

    It inherits from :class:`Flow <raider.flow.Flow>` so it contains
    one ``request``, the ``response``, the ``outputs`` that needs to
    be extracted from the response, and a list of ``operations`` to be
    run when the exchange is over.

    Use this only when working with requests that *DO* change the
    authentication state.  It's used in the :class:`Authentication
    <raider.authentication.Authentication>` class to run actions that
    affect the authentication state.

    When the authentication state doesn't change, use :class:`Flow
    <raider.flow.Flow>` objects.

    Attributes:
      request:
        A :class:`Request <raider.request.Request>` object detailing the
        HTTP request with its elements.
      response:
        A :class:`requests.model.Response` object. It's empty until the
        request is sent. When the HTTP response arrives, it's stored
        here.
      outputs:
        A list of :class:`Plugin <raider.plugins.Plugin>` objects
        detailing the pieces of information to be extracted from the
        response. Those will be later available for other Flow objects.
      operations:
        A list of :class:`Operation <raider.operations.Operation>`
        objects to be executed after the response is received and
        outputs are extracted. Should contain a :class:`NextStage
        <raider.operations.NextStage>` operation if another Flow is
        expected.

    """
    def __init__(
        self,
        request: Request,
        outputs: Optional[List[Plugin]] = None,
        operations: Optional[List[Operation]] = None,
    ) -> None:

        super().__init__(
            request=request, outputs=outputs, operations=operations
        )
