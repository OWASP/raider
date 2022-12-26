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
"""Plugin to work with cookies.
"""

import re
from functools import partial
from typing import Callable, Optional

import requests

from raider.plugins.common import Plugin


class Cookie(Plugin):
    """:class:`Plugin <raider.plugins.common.Plugin>` dealing with the
    :class:`Cookies <raider.plugins.basic.Cookie>` in HTTP
    :term:`Requests <Request>` and :term:`Responses <Response>`.

    Use the :class:`Cookie` :class:`Plugin` when working with the data
    found in :class:`Cookie` headers.

    Attributes:
      name:
        A String with the :class:`Cookie's <Cookie>` name. Also used
        as an identifier for the :class:`Plugin
        <raider.plugins.common.Plugin>`
      function:
        A Callable which will be called to extract the ``value`` of
        the :class:`Cookie` when used as an input in a :ref:`Flow
        <flows>`. The function should set ``self.value`` and also
        return it.
      name_function:
        A Callable which will be called to extract the ``name`` of the
        :class:`Cookie` when it's not known in advance and the flag
        ``NAME_NOT_KNOWN_IN_ADVANCE`` is set.
      plugins:
        A List of :class:`Plugins <Plugin>` whose ``value`` needs to
        be extracted first before current :class:`Cookie's <Cookie>`
        value can be extracted. Used when the flag
        ``DEPENDS_ON_OTHER_PLUGINS`` is set.
      value:
        A string containing the :class:`Cookie's <Cookie>` output
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
        """Initializes the :class:`Cookie` :class:`Plugin
        <raider.plugins.common.Plugin>`.

        Creates a :class:`Cookie` :class:`Plugin
        <raider.plugins.common.Plugin>`, either with predefined
        ``value``, or by using a ``function`` defining how the
        ``value`` should be generated on runtime.

        Args:
          name:
            A String with the name of the :class:`Cookie`.
          value:
            An Optional String with the ``value`` of the
            :class:`Cookie` in case it's already known.
          function:
            A Callable which is used to get the ``value`` of the
            :class:`Cookie` on runtime.
          flags:
            An integer containing the ``flags`` that define the
           :class:`Plugin's <raider.plugins.common.Plugin>`
           behaviour. By default only ``NEEDS_RESPONSE`` flag is set.

        """
        if not function and (flags & Plugin.NEEDS_RESPONSE):
            function = self.extract_cookie_from_response
        super().__init__(
            name=name, function=function, value=value, flags=flags
        )

    def extract_cookie_from_response(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Returns the :class:`Cookie` with the specified name from
        the response.

        Args:
          response:
            A :class:`requests.models.Response` object containing the
            HTTP :term:`Response`.

        Returns:
          An Optional String with the :class:`Cookie`
          ``value``. Returns None if no such :class:`Cookie` found.

        """
        return response.cookies.get(self.name)

    def __str__(self) -> str:
        """Returns a string representation of the :class:`Cookie`.

        Used for logging purposes only.
        """
        return str({self.name: self.value})

    @classmethod
    def regex(cls, regex: str) -> "Cookie":
        """Extracts the :class:`Cookie` using regular expressions.

        When the name of the :class:`Cookie` is unknown in advance,
        but can be matched against a regular expression, you can use
        ``Cookie.regex`` to extract it. The ``name`` of the
        :class:`Cookie` should be supplied as a regular expression
        inside a group, i.e. between ``(`` and ``)``.

        For example the following code will match the :class:`Cookie`
        whose ``name`` is a 10 character string containing letters and
        digits:

        .. code-block:: hylang

           (setv csrf_token
                   (Cookie.regex "([a-zA-Z0-9]{10})"))


        Args:
          regex:
            A String with the regular expression to match the name of
            the :class:`Cookie`.

        Returns:
          A :class:`Cookie` object configured to match the regular
          expression.

        """

        def extract_cookie_value_regex(
            response: requests.models.Response,
            regex: str,
        ) -> Optional["str"]:
            """Finds the :class:`Cookie` ``value`` matching the given
            ``regex``.

            Args:
              response:
                A :class:`requests.models.Response` object with the
                HTTP :term:`Response`.
              regex:
                A String containing the regular expression to match for.

            Returns:
              An Optional String with the ``value`` extracted from the
              :class:`Cookie` matching the ``name`` with the supplied
              ``regex``.

            """
            for name, value in response.cookies.items():
                if re.search(regex, name):
                    return value
            return None

        def extract_cookie_name_regex(
            response: requests.models.Response,
            regex: str,
        ) -> Optional["str"]:
            """Find the :class:`Cookie` ``name`` matching the given
            ``regex``.

            Args:
              response:
                A :class:`requests.models.Response` object with the
                HTTP :term:`Response`.
              regex:
                A String containing the regular expression to match for.

            Returns:
              An Optional String with the ``name`` extracted from the
              :class:`Cookie` matching the ``name`` with the supplied
              ``regex``.

            """
            for name in response.cookies.keys():
                if re.search(regex, name):
                    return name
            return None

        cookie = cls(
            name=regex,
            function=partial(extract_cookie_value_regex, regex=regex),
            flags=Plugin.NEEDS_RESPONSE | Plugin.NAME_NOT_KNOWN_IN_ADVANCE,
        )

        cookie.name_function = partial(extract_cookie_name_regex, regex=regex)

        return cookie

    @classmethod
    def from_plugin(cls, parent_plugin: Plugin, name: str) -> "Cookie":
        """Creates a :class:`Cookie` from another :class:`Plugin
        <raider.plugins.common.Plugin>`.

        Given another :class:`Plugin <raider.plugins.common.Plugin>`,
        and a ``name``, create a :class:`Cookie
        <raider.plugins.basic.Cookie>`.

        For example, if we need to extract the ``access_token`` from JSON:

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

        And use it later as a :class:`Cookie`:

        .. code-block:: hylang

           (setv my_function
             (Flow
               :request (Request
                          :method "GET"
                          :url "https://www.example.com/my_function"

                          ;; Sends the cookie `mycookie` with the value of
                          ;; `access_token` extracted from JSON.
                          :cookies [(Cookie.from_plugin
                                      access_token
                                      "mycookie" )])))


        Args:
          name:
            The :class:`Cookie` ``name`` to use.
          plugin:
            The :class:`Plugin <raider.plugins.common.Plugin>` which
            will contain the ``value`` we need.

        Returns:
          A :class:`Cookie` object with the ``name`` and the
          :class:`Plugin's <raider.plugins.common.Plugin>` ``value``.

        """
        cookie = cls(
            name=name,
            value=parent_plugin.value,
            function=lambda: parent_plugin.value,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )
        cookie.plugins.append(parent_plugin)
        return cookie

