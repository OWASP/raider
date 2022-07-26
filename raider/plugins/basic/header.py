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
"""Plugin to work with headers.
"""
import re
from base64 import b64encode
from functools import partial
from typing import Callable, Optional

import requests

from raider.plugins.common import Plugin


class Header(Plugin):
    """

    Use this Plugin when dealing with the headers in the HTTP request.

    """

    def __init__(
        self,
        name: str,
        value: Optional[str] = None,
        function: Optional[Callable[..., Optional[str]]] = None,
        flags: int = Plugin.NEEDS_RESPONSE,
    ) -> None:
        """Initializes the Header Plugin.

        Creates a Header Plugin, either with predefined ``value``, or by
        using a function defining how the ``value`` should be generated on
        runtime.

        Args:
          name:
            A string with the name of the Header.
          value:
            An optional string with the ``value`` of the Header in case it's
            already known.
          function:
            A Callable function which is used to get the ``value`` of the
            Header on runtime.

        """

        if not function and (flags & Plugin.NEEDS_RESPONSE):
            function = self.extract_header_from_response
        super().__init__(
            name=name, function=function, value=value, flags=flags
        )

    def extract_header_from_response(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Returns the header with the specified name from the response."""
        return response.headers.get(self.name)

    def __str__(self) -> str:
        """Returns a string representation of the Plugin."""
        return str({self.name: self.value})

    @classmethod
    def regex(cls, regex: str) -> "Header":
        """Extract the header using regular expressions."""

        def extract_header_value_regex(
            response: requests.models.Response,
            regex: str,
        ) -> Optional["str"]:
            """Find the header ``value`` matching the given regex."""
            for name, value in response.headers.items():
                if re.search(regex, name):
                    return value
            return None

        def extract_header_name_regex(
            response: requests.models.Response,
            regex: str,
        ) -> Optional["str"]:
            """Find the header name matching the given regex."""
            for name in response.headers.keys():
                if re.search(regex, name):
                    return name
            return None

        header = cls(
            name=regex,
            function=partial(extract_header_value_regex, regex=regex),
            flags=Plugin.NEEDS_RESPONSE | Plugin.NAME_NOT_KNOWN_IN_ADVANCE,
        )

        header.name_function = partial(extract_header_name_regex, regex=regex)

        return header

    @classmethod
    def basicauth(cls, username: str, password: str) -> "Header":
        """Creates a basic authentication header.

        Given the username and the password for the basic
        authentication, returns the Header object with the proper ``value``.

        Args:
          username:
            A string with the basic authentication username.
          password:
            A string with the basic authentication password.

        Returns:
          A Header object with the encoded basic authentication string.

        """
        encoded = b64encode(":".join([username, password]).encode("utf-8"))
        header = cls("Authorization", "Basic " + encoded.decode("utf-8"))
        return header

    @classmethod
    def bearerauth(cls, access_token: Plugin) -> "Header":
        """Creates a bearer authentication header.

        Given the access_token as a Plugin, extracts its ``value`` and
        returns a Header object with the correct ``value`` to be passed as
        the Bearer Authorization string in the Header.

        Args:
          access_token:
            A Plugin containing the ``value`` of the token to use.

        Returns:
          A Header object with the proper bearer authentication string.

        """
        header = cls(
            name="Authorization",
            value=None,
            flags=0,
            function=lambda: "Bearer " + access_token.value
            if access_token.value
            else None,
        )
        return header

    @classmethod
    def from_plugin(cls, parent_plugin: Plugin, name: str) -> "Header":
        """Creates a Header from a Plugin.

        Given another :class:`plugin <raider.plugins.Plugin>`, and a
        name, create a :class:`header <raider.plugins.Header>`.

        Args:
          name:
            The header name to use.
          plugin:
            The plugin which will contain the ``value`` we need.

        Returns:
          A Header object with the name and the plugin's ``value``.

        """
        header = cls(
            name=name,
            value=parent_plugin.value,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )
        header.plugins = [parent_plugin]
        header.function = lambda: header.plugins[0].value
        return header
