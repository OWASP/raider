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
"""Plugin to read from files.
"""
from functools import partial
from typing import Callable, Optional, Union

from raider.plugins.common import Plugin


class File(Plugin):
    """:class:`Plugin <raider.plugins.common.Plugin>` used for getting
    data from the filesystem.

    Use :class:`File`: :class:`Plugin <raider.plugins.common.Plugin>`
    when needing to upload something, or sending a :term:`Request`
    with lots of data that would better be stored on the filesystem
    instead of :term:`hyfiles`.

    Attributes:
      name:
        A String with the :class:`Plugin's
        <raider.plugins.common.Plugin>` name. For :class:`File`
        objects that's the ``path`` to the file.
      function:
        A Callable which will be called to extract the ``value`` of
        the :class:`Plugin` when used as an input in a :ref:`Flow
        <flows>`. The function should set ``self.value`` and also
        return it. By default for :class:`File` :class:`Plugins
        <raider.plugins.common.Plugin>` it puts the unmodified
        contents of the :class:`File` found in the ``path``.
      name_function:
        A Callable which will be called to extract the ``name`` of the
        :class:`Plugin` when it's not known in advance and the flag
        ``NAME_NOT_KNOWN_IN_ADVANCE`` is set. :class:`File` doesn't
        use this.
      plugins:
        A List of :class:`Plugins <Plugin>` whose ``value`` needs to be
        extracted first before current :class:`Cookie's <Cookie>`
        value can be extracted. Used when the flag
        ``DEPENDS_ON_OTHER_PLUGINS`` is set.
      value:
        A string containing the :class:`File's <File>` output
        ``value`` to be used as input in the HTTP :term:`Requests
        <Request>` which is just the :class:`File` contents.
      flags:
        An integer containing the flags that define the
        :class:`Plugin's <raider.plugins.common.Plugin>`
        behaviour. For :class:`File` :class:`Plugins no flags are set
        by default.

    """

    def __init__(
        self,
        path: str,
        function: Callable[..., Optional[Union[str, bytes]]] = None,
        flags: int = 0,
    ) -> None:

        """Initializes the :class:`File` :class:`Plugin
        <raider.plugins.common.Plugin>`.

        Creates a :class:`File` :class:`Plugin
        <raider.plugins.common.Plugin>`, and populates its ``value``
        with the contents of a :class:`File`` from the filesystem.

        Args:
          path:
            A String with the path of the :class:`File`.
          function:
            An Optional Callable which is used to get the ``value`` of
            the :class:`File` on runtime.
          flags:
            An integer containing the ``flags`` that define the
           :class:`Plugin's <raider.plugins.common.Plugin>`
           behaviour. By default no flag is set.

        """
        self.path = path

        if not function:
            super().__init__(name=path, function=self.read_file, flags=flags)
        else:
            super().__init__(name=path, function=function, flags=flags)

    def read_file(self) -> bytes:
        """Sets the :class:`Plugin's <raider.plugins.common.Plugin>`
        ``value`` to the file contents.

        Returns:
          A Bytes string containing the raw file contents.
        """
        with open(self.path, "rb") as finput:
            self.value = finput.read()
        return self.value

    @classmethod
    def replace(
        cls, path: str, old_value: str, new_value: Union[str, int, Plugin]
    ) -> "File":
        """Read a :class:`File` and replace strings with new ``value``s.

        Use this in case the :class:`File` is a template that needs
        some part of it replaced with a new string, for example:

        If we have the file ``data.json``:

        .. code-block::

           {"data":
              "username": $USERNAME$,
              "nickname": "nickname",
              [...]
           }

        And we want to replace ``$USERNAME$`` with the real username,
        we can use:

        .. code-block::

           (File.replace "/path/to/data.json"
              "$USERNAME$"
              "admin")

        To replace every instance of ``$USERNAME$`` with our chosen
        ``value`` in ``new_value``.

        Args:
          path:
            A String with the ``path`` of the :class:`File`.
          old_value:
            A String with the old ``value`` to be replaced.
          new_value:
            A String with the new ``value`` to be replaced.

        """

        def replace_string(
            original: bytes, old: str, new: Union[str, int, Plugin]
        ) -> Optional[bytes]:
            if isinstance(new, Plugin):
                if not new.value:
                    return None
                return original.replace(
                    old.encode("utf-8"), new.value.encode("utf-8")
                )
            return original.replace(
                old.encode("utf-8"), str(new).encode("utf-8")
            )

        with open(path, "rb") as finput:
            file_contents = finput.read()

        file_replace_plugin = cls(
            path=path,
            function=partial(
                replace_string,
                original=file_contents,
                old=old_value,
                new=new_value,
            ),
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )

        if isinstance(new_value, Plugin):
            file_replace_plugin.plugins.append(new_value)

        return file_replace_plugin
