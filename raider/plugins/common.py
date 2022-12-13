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
"""Common Plugin classes used by other plugins.
"""


import logging
from typing import Callable, Dict, List, Optional

import requests


class Plugin:
    """Parent class for all :class:`Plugins <Plugin>`.

    Each :class:`Plugin` class inherits from here. ``get_value``
    function should be called when extracting the ``value`` from the
    :class:`Plugin`, which will then be stored in the ``value``
    attribute.

    :class:`Plugin's <Plugin>` behaviour can be controlled using
    following flags:

    ``NEEDS_USERDATA`` = 0x01
      When set, the :class:`Plugin` will get its ``value`` from the
      user's data, which will be sent to the function defined
      here. Use when :class:`Plugin's <Plugin>` ``value`` depends on
      things defined in the :class:`User` class, like the username or
      password.
    ``NEEDS_RESPONSE`` = 0x02
      When set, the :class:`Plugin's <Plugin>` ``value`` can only be
      extracted from a previous HTTP response.
    ``DEPENDS_ON_OTHER_PLUGINS`` = 0x04
      When set, the :class:`Plugin's <Plugin>` ``value`` can only be
      extracted from other :class:`Plugins <Plugin>`. Use this when
      combining :class:`Plugins <Plugin>`.
    ``NAME_NOT_KNOWN_IN_ADVANCE`` = 0x08
      When set, the name of the :class:`Plugin` is not known in
      advance, and will be set when the :class:`Plugin` runs. Useful
      when the name changes and can only be matched with a regex.


    Attributes:
      name:
        A String used as an identifier for the :class:`Plugin`.
      function:
        A Callable which will be called to extract the ``value`` of
        the :class:`Plugin` when used as an input in a :ref:`Flow
        <flows>`. The function should set ``self.value`` and also
        return it.
      name_function:
        A Callable which will be called to extract the ``name`` of the
        :class:`Plugin` when it's not known in advance and the flag
        ``NAME_NOT_KNOWN_IN_ADVANCE`` is set.
      plugins:
        A List of :class:`Plugins <Plugin>` whose value needs to be
        extracted first before current :class:`Plugin's <Plugin>`
        value can be extracted. Used when the flag
        ``DEPENDS_ON_OTHER_PLUGINS`` is set.
      value:
        A String containing the :class:`Plugin's <Plugin>` output
        ``value`` to be used as input in the HTTP :term:`Requests
        <Request>`.
      flags:
        An Integer containing the flags that define the
        :class:`Plugin's <Plugin>` behaviour.

    """

    # Plugin flags
    NEEDS_USERDATA = 0x01
    NEEDS_RESPONSE = 0x02
    DEPENDS_ON_OTHER_PLUGINS = 0x04
    NAME_NOT_KNOWN_IN_ADVANCE = 0x08

    def __init__(
        self,
        name: str,
        function: Optional[Callable[..., Optional[str]]] = None,
        value: Optional[str] = None,
        flags: int = 0,
    ) -> None:
        """Initializes a :class:`Plugin` object.

        Creates a :class:`Plugin` object, holding a ``function``
        defining how to extract the ``value``.

        Args:
          name:
            A String with the unique identifier of the :class:`Plugin`.
          function:
            An Optional Callable that will be used to extract the
            :class:`Plugin's <Plugin>` ``value``.
          value:
            An Optional String with the predefined ``value`` of the
            :class:`Plugin`.
          flags:
            An Integer containing the flags that define the
            :class:`Plugin's <Plugin>` behaviour. No flags are set by
            default

        """
        self.name = name
        self.plugins: List["Plugin"] = []
        self.value: Optional[str] = value
        self.flags = flags
        self.logger = None

        self.function: Callable[..., Optional[str]]
        self.name_function: Optional[Callable[..., Optional[str]]] = None

        if (flags & Plugin.NEEDS_USERDATA) and not function:
            self.function = self.extract_value_from_userdata
        elif not function:
            self.function = self.return_value
        else:
            self.function = function

    def get_value(self, pconfig) -> Optional[str]:
        """Gets the ``value`` from the :class:`Plugin`.

        Depending on the :class:`Plugin's <Plugin>` flags, extract and
        return its ``value``.

        Args:
          userdata:
            A Dictionary with the user specific data.

        Returns:
          An Optional String with the value of the
          :class:`Plugin`. Returns None if no value can be extracted.

        """
        if not self.needs_response:
            if self.needs_userdata:
                self.value = self.function(pconfig.active_user.to_dict())
            elif self.depends_on_other_plugins:
                for item in self.plugins:
                    item.get_value(pconfig)
                self.value = self.function()
            else:
                self.value = self.function()
        return self.value

    def extract_value_from_response(
        self,
        response: Optional[requests.models.Response],
    ) -> None:
        """Extracts the ``value`` of the :class:`Plugin` from the HTTP response.

        If ``NEEDS_RESPONSE`` flag is set, the :class:`Plugin` will
        extract its ``value`` upon receiving the HTTP response, and store
        it inside the ``value`` attribute.

        Args:
          response:
            An :class:`requests.models.Response` object with the HTTP
            response.

        """
        output = self.function(response)
        if output:
            self.value = output
            logging.debug(
                "Found ouput %s = %s",
                self.name,
                self.value,
            )
        else:
            logging.warning("Couldn't extract output: %s", str(self.name))

    def extract_name_from_response(
        self,
        response: Optional[requests.models.Response],
    ) -> None:
        """Extracts the name of the :class:`Plugin` from the HTTP response.

        If ``NAME_NOT_KNOWN_IN_ADVANCE`` flag is set, the :class:`Plugin`
        will set its name after receiving the HTTP response, and store
        it inside the ``name`` attribute.

        Args:
          response:
            An :class:`requests.models.Response` object with the HTTP
            response.

        """
        if callable(self.name_function):
            # pylint can't figure out name_function is callable
            # pylint: disable=E1102
            output = self.name_function(response)
            if output:
                self.name = output
        else:
            logging.warning("Couldn't extract name: %s", str(self.name))

    def extract_value_from_userdata(self, pconfig) -> Optional[str]:
        """Extracts the :class:`Plugin` ``value`` from userdata.

        Given a dictionary with the userdata, return its ``value`` with the
        same name as the "name" attribute from this :class:`Plugin`.

        Args:
          data:
            A Dictionary with user specific data.

        Returns:
          An Optional String with the ``value`` of the variable
          found. Returns None if it cannot be extracted.

        """
        data = pconfig.active_user.to_dict()
        if data and self.name in data:
            self.value = data[self.name]
        return self.value

    def return_value(self) -> Optional[str]:
        """Returns :class:`Plugin's <Plugin>` ``value``.

        This is used when needing a function just to return the ``value``.

        Returns:
          An Optional String with the stored ``value``. Returns None
          if ``value`` is empty.

        """
        return self.value

    @property
    def needs_userdata(self) -> bool:
        """Returns True if the ``NEEDS_USERDATA`` flag is set."""
        return bool(self.flags & self.NEEDS_USERDATA)

    @property
    def needs_response(self) -> bool:
        """Returns True if the ``NEEDS_RESPONSE`` flag is set."""
        return bool(self.flags & self.NEEDS_RESPONSE)

    @property
    def depends_on_other_plugins(self) -> bool:
        """Returns True if the ``DEPENDS_ON_OTHER_PLUGINS`` flag is set."""
        return bool(self.flags & self.DEPENDS_ON_OTHER_PLUGINS)

    @property
    def name_not_known_in_advance(self) -> bool:
        """Returns True if the ``NAME_NOT_KNOWN_IN_ADVANCE`` flag is set."""
        return bool(self.flags & self.NAME_NOT_KNOWN_IN_ADVANCE)


class Parser(Plugin):
    """Parent class for :class:`Parser` :class:`Plugins <Plugin>`.

    Use the :class:`Parser` :class:`Plugin` when needing to take
    another :class:`Plugin` as input, build a data structure out of
    it, and extracting some parts you're interested in. The simplest
    example would be parsing a URL to extract the domain name from it.

    Attributes:
      name:
        A String used as an identifier for the :class:`Parser`.
      function:
        A Callable which will be called to parse the ``value`` of
        parent :class:`Plugin` and extract the new ``value``. The
        function should set ``self.value`` and also return it.
      name_function:
        A Callable which will be called to extract the ``name`` of the
        :class:`Plugin` when it's not known in advance and the flag
        ``NAME_NOT_KNOWN_IN_ADVANCE`` is set. By default not used in
        :class:`Parser` :class:`Plugin`.
      plugins:
        A List of :class:`Plugins <Plugin>` whose value needs to be
        extracted first before current :class:`Plugin's <Plugin>`
        value can be extracted. Used when the flag
        ``DEPENDS_ON_OTHER_PLUGINS`` is set, which it is by default
        for :class:`Parsers <Parser>`.
      value:
        A String containing the :class:`Parser's <Parser>` output
        ``value`` to be used as input in the HTTP :term:`Requests
        <Request>`.
      flags:
        An Integer containing the flags that define the
        :class:`Plugin's <Plugin>` behaviour. By default only the
        ``DEPENDS_ON_OTHER_PLUGINS`` flag is set.

    """

    def __init__(
        self,
        name: str,
        function: Callable[[], Optional[str]],
        value: str = None,
    ) -> None:
        """Initializes the :class:`Parser` :class:`Plugin`.

        Creates a :class:`Parser` object, holding a ``function``
        defining how to parse the parent :class:`Plugin` in order to
        extract the ``value``. Only the flag
        ``DEPENDS_ON_OTHER_PLUGINS`` is preset, since it needs to
        extract the ``value`` from other :class:`Plugins <Plugin>`, and
        those need to be extracted first.

        Args:
          name:
            A String with the unique identifier of the :class:`Parser`.
          function:
            A Callable function that will be used to extract the
            :class:`Parser's <Parser>` ``value``.
          value:
            A String with the extracted ``value`` from the :class:`Plugin`.

        """
        super().__init__(
            name=name,
            value=value,
            function=function,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )


class Processor(Plugin):
    """Parent class for :class:`Processor` :class:`Plugins <Plugin>`.

    Use the :class:`Processor` :class:`Plugin` when needing to take
    another :class:`Plugin` as input, and modify (process) it to get
    the needed ``value``. For example by encoding/decoding or doing
    other kinds of modifications to the ``value`` extracted from the
    parent :class:`Plugin`.

    Attributes:
      name:
        A String used as an identifier for the :class:`Processor`.
      function:
        A Function which will be called to process the ``value`` of
        the parent :class:`Plugin` and get the new ``value``. The
        function should set ``self.value`` and also return it.
      name_function:
        A Callable which will be called to extract the ``name`` of the
        :class:`Plugin` when it's not known in advance and the flag
        ``NAME_NOT_KNOWN_IN_ADVANCE`` is set. By default not used in
        :class:`Parser` :class:`Plugin`.
      plugins:
        A List of :class:`Plugins <Plugin>` whose value needs to be
        extracted first before current :class:`Plugin's <Plugin>`
        value can be extracted. Used when the flag
        ``DEPENDS_ON_OTHER_PLUGINS`` is set, which it is by default
        for :class:`Processors <Processor>`.
      value:
        A String containing the :class:`Processors's <Processor>`
        output ``value`` to be used as input in the HTTP
        :term:`Requests <Request>`.
      flags:
        An Integer containing the flags that define the
        :class:`Plugin's <Plugin>` behaviour. By default only the flag
        ``DEPENDS_ON_OTHER_PLUGINS`` is set.

    """

    def __init__(
        self,
        name: str,
        function: Callable[[], Optional[str]],
        value: Optional[str] = None,
    ) -> None:
        """Initializes the :class:`Processor` :class:`Plugin`.

        Creates a :class:`Processor` object, holding a ``function``
        defining how to process the parent :class:`Plugin` to get the
        ``value``. Only the flag ``DEPENDS_ON_OTHER_PLUGINS`` is
        preset, since it needs to extract the ``value`` from other
        :class:`Plugins <Plugin>`, and those need to be extracted first.

        Args:
          name:
            A String with the unique identifier of the :class:`Parser`.
          function:
            A Callable that will be used to extract the
            :class:`Parsers <Parser>` ``value``.
          value:
            A String with the extracted ``value`` from the :class:`Plugin`.

        """
        super().__init__(
            name=name,
            value=value,
            function=function,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )


class Empty(Plugin):
    """Class for :class:`Empty` :class:`Plugins <Plugin>`.

    Use the :class:`Empty` :class:`Plugin` when you don't care about
    the actual ``value`` of the :class:`Plugin`, and only want to have a
    placeholder to use for fuzzing.

    Attributes:
      name:
        A String used as an identifier for the :class:`Empty`
        :class:`Plugin`.
      function:
        A Callable which will be called to process the ``value`` of
        the parent :class:`Plugin` and get the new ``value``. The
        function should set ``self.value`` and also return it.
      name_function:
        A Callable which will be called to extract the ``name`` of the
        :class:`Plugin` when it's not known in advance and the flag
        ``NAME_NOT_KNOWN_IN_ADVANCE`` is set. Not used in
        :class:`Empty` :class:`Plugin`.
      plugins:
        A List of :class:`Plugins <Plugin>` whose value needs to be
        extracted first before current :class:`Plugin's <Plugin>`
        value can be extracted. Used when the flag
        ``DEPENDS_ON_OTHER_PLUGINS`` is set. Not used in
        :class:`Empty` :class:`Plugin`.
      value:
        A string containing the :class:`Processors's <Processor>`
        output ``value`` to be used as input in the HTTP
        :term:`Requests <Request>`. Not used in :class:`Empty`
        :class:`Plugin`.
      flags:
        An integer containing the flags that define the
        :class:`Plugin's <Plugin>` behaviour. Not used in
        :class:`Empty` :class:`Plugin`.

    """

    def __init__(self, name: str):
        """Initializes the :class:`Empty` :class:`Plugin`.

        Creates an :class:`Empty` object without any ``value``. Use it
        when you don't need any ``value`` for the :class:`Plugin` and only
        want to use it as a placeholder for fuzzing.

        Args:
          name:
            A String with the unique identifier of the :class:`Parser`.

        """
        super().__init__(
            name=name,
            flags=0,
        )
