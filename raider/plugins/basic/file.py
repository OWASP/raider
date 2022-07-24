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
"""
"""
from functools import partial
from typing import Callable, Optional, Union

from raider.plugins.common import Plugin


class File(Plugin):
    """

    Use this plugin to manipulate files.

    """

    def __init__(
        self,
        path: str,
        function: Callable[..., Optional[Union[str, bytes]]] = None,
        flags: int = 0,
    ) -> None:
        """Initializes the File Plugin.

        Creates a File Plugin which will set its ``value`` to the contents
        of the file.

        Args:
          path:
            A string containing the file path.

        """
        self.path = path

        if not function:
            super().__init__(name=path, function=self.read_file, flags=flags)
        else:
            super().__init__(name=path, function=function, flags=flags)

    def read_file(self) -> bytes:
        """Sets the plugin's ``value`` to the file content."""
        with open(self.path, "rb") as finput:
            self.value = finput.read()
        return self.value

    @classmethod
    def replace(
        cls, path: str, old_value: str, new_value: Union[str, int, Plugin]
    ) -> "File":
        """Read a file and replace strings with new ``value``s."""

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
