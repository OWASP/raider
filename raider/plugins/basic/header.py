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
"""Plugin to work with headers.
"""
import re
from base64 import b64encode
from functools import partial
from typing import Callable, Optional

import requests

from raider.plugins.common import Plugin


class Header(Plugin):
    """:class:`Plugin <raider.plugins.common.Plugin>` dealing with the
    :class:`Headers <raider.plugins.basic.Header>` in HTTP
    :term:`Requests <Request>` and :term:`Responses <Response>`.

    Use the :class:`Header` :class:`Plugin
    <raider.plugins.basic.Plugin>` when working with the data found in
    HTTP :class:`Headers <Header>`.

    Attributes:
      name:
        A String with the :class:`Header's <Header>` name. Also used
        as an identifier for the :class:`Plugin
        <raider.plugins.common.Plugin>`
      function:
        A Callable which will be called to extract the ``value`` of
        the :class:`Header` when used as an input in a :ref:`Flow
        <flows>`. The function should set ``self.value`` and also
        return it.
      name_function:
        A Callable which will be called to extract the ``name`` of the
        :class:`Header` when it's not known in advance and the flag
        ``NAME_NOT_KNOWN_IN_ADVANCE`` is set.
      plugins:
        A List of :class:`Plugins <Plugin>` whose ``value`` needs to be
        extracted first before current :class:`Header's <Header>`
        value can be extracted. Used when the flag
        ``DEPENDS_ON_OTHER_PLUGINS`` is set.
      value:
        A string containing the :class:`Header's <Header>` output
        ``value`` to be used as input in the HTTP :term:`Requests
        <Request>`.
      flags:
        An integer containing the ``flags`` that define the
        :class:`Plugin's <raider.plugins.common.Plugin>` behaviour.

    """

    def __init__(
        self,
        name: str,
        value: Optional[str] = None,
        function: Optional[Callable[..., Optional[str]]] = None,
        flags: int = Plugin.NEEDS_RESPONSE,
    ) -> None:
        """Initializes the :class:`Header` :class:`Plugin
        <raider.plugins.common.Plugin>`.

        Creates a :class:`Header` :class:`Plugin
        <raider.plugins.common.Plugin>`, either with predefined
        ``value``, or by using a ``function`` defining how the
        ``value`` should be generated on runtime.

        Args:
          name:
            A String with the name of the :class:`Header`.
          value:
            An Optional String with the ``value`` of the
            :class:`Header` in case it's already known.
          function:
            A Callable which is used to get the ``value`` of the
            :class:`Header` on runtime.
          flags:
            An integer containing the ``flags`` that define the
           :class:`Plugin's <raider.plugins.common.Plugin>`
           behaviour. By default only ``NEEDS_RESPONSE`` flag is set.

        """

        if not function and (flags & Plugin.NEEDS_RESPONSE):
            function = self.extract_header_from_response
        super().__init__(
            name=name, function=function, value=value, flags=flags
        )

    def extract_header_from_response(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Returns the :class:`Header` with the specified name from
        the response.

        Args:
          response:
            A :class:`requests.models.Response` object containing the
            HTTP :term:`Response`.

        Returns:
          An Optional String with the :class:`Header`
          ``value``. Returns None if no such :class:`Header` found.

        """
        return response.headers.get(self.name)

    def __str__(self) -> str:
        """Returns a string representation of the :class:`Header`.

        Used for logging purposes only.
        """
        return str({self.name: self.value})

    @classmethod
    def regex(cls, regex: str) -> "Header":
        """Extracts the :class:`Header` using regular expressions.

        When the name of the :class:`Header` is unknown in advance,
        but can be matched against a regular expression, you can use
        ``Header.regex`` to extract it. The ``name`` of the
        :class:`Header` should be supplied as a regular expression
        inside a group, i.e. between ``(`` and ``)``.

        For example the following code will match the :class:`Header`
        whose ``name`` is a 10 character string containing letters and
        digits:

        .. code-block:: hylang

           (setv csrf_token
                   (Header.regex "([a-zA-Z0-9]{10})"))


        Args:
          regex:
            A String with the regular expression to match the name of
            the :class:`Header`.

        Returns:
          A :class:`Header` object configured to match the regular
          expression.

        """

        def extract_header_value_regex(
            response: requests.models.Response,
            regex: str,
        ) -> Optional["str"]:
            """Finds the :class:`Header` ``value`` matching the given
            ``regex``.

            Args:
              response:
                A :class:`requests.models.Response` object with the
                HTTP :term:`Response`.
              regex:
                A String containing the regular expression to match for.

            Returns:
              An Optional String with the ``value`` extracted from the
              :class:`Header` matching the ``name`` with the supplied
              ``regex``.

            """
            for name, value in response.headers.items():
                if re.search(regex, name):
                    return value
            return None

        def extract_header_name_regex(
            response: requests.models.Response,
            regex: str,
        ) -> Optional["str"]:
            """Find the :class:`Header` ``name`` matching the given
            ``regex``.

            Args:
              response:
                A :class:`requests.models.Response` object with the
                HTTP :term:`Response`.
              regex:
                A String containing the regular expression to match for.

            Returns:
              An Optional String with the ``name`` extracted from the
              :class:`Header` matching the ``name`` with the supplied
              ``regex``.

            """
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
        """Creates a basic authentication :class:`Header`.

        Given the username and the password for the basic
        authentication, returns the :class:`Header` object with the
        proper ``value``, i.e. with the ``name`` as ``Authorization``
        and the ``value`` as ``Basic `` followed by base64 encoded
        ``username:password``.

        For example:

        .. code-block:: hylang

           (setv my_function
             (Flow
               :request
                 (Request
                   :method "GET"
                   :url "https://www.example.com/my_function"
                   :headers [(Header.basicauth "username" "password")])))

        Args:
          username:
            A String with the basic authentication ``username``.
          password:
            A String with the basic authentication ``password``.

        Returns:
          A :class:`Header` object with the encoded basic
          authentication string.

        """
        encoded = b64encode(":".join([username, password]).encode("utf-8"))
        header = cls("Authorization", "Basic " + encoded.decode("utf-8"))
        return header

    @classmethod
    def bearerauth(cls, access_token: Plugin) -> "Header":
        """Creates a bearer authentication :class:`Header`.

        Given the ``access_token`` as a :class:`Plugin
        <raider.plugins.common.Plugin>`, extracts its ``value`` and
        returns a :class:`Header` object with the correct ``value`` to
        be passed as the Bearer Authorization string in the
        :class:`Header`, i.e. with the ``name`` as ``Authorization``
        and the ``value`` as ``Bearer `` followed by the value from
        parent :class:`Plugin <raider.plugins.common.Plugin>`

        For example if we extract the ``access_token`` from JSON:

        .. code-block:: hylang

           (setv access_token
             (Json
               :name "access_token"
               :extract "token"))

           (setv get_token
              (Flow
                :request
                  (Request
                    :method "POST"
                    :url "https://www.example.com/login"
                    :data {"username" "username"
                           "password" "password"})
                 :outputs [access_token]))


        And use it later as a bearer authentication :class:`Header`:

        .. code-block:: hylang

           (setv my_function
             (Flow
               :request
                 (Request
                   :method "GET"
                   :url "https://www.example.com/my_function"
                   :headers [(Header.bearerauth access_token)])))


        Args:
          access_token:
            A :class:`Plugin <raider.plugins.common.Plugin>`
            containing the ``value`` of the token to use.

        Returns:
          A :class:`Header` object with the proper bearer
          authentication string.

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
        """Creates a :class:`Header` from another :class:`Plugin
        <raider.plugins.common.Plugin>`.

        Given another :class:`Plugin <raider.plugins.common.Plugin>`,
        and a ``name``, create a :class:`Header`. Unlike
        :func:`~Header.basicauth` and :func:`~Header.bearerauth` no
        string will be added to the beginning of :class:`Header`
        ``value``, so this class method can be used for other
        arbitrary :class:`Headers <Header>` not just ``Authorization``
        ones.

        Args:
          name:
            The :class:`Header` ``name`` to use.
          plugin:
            The :class:`Plugin <raider.plugins.common.Plugin>` which
            will contain the ``value`` we need.

        Returns:
          A :class:`Header` object with the ``name`` and the
          :class:`Plugin's <raider.plugins.common.Plugin>` ``value``.

        """
        header = cls(
            name=name,
            value=parent_plugin.value,
            function=lambda: parent_plugin.value,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )
        header.plugins.append(parent_plugin)
        return header
