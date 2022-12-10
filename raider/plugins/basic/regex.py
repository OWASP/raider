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
"""Plugin to extract regular expressions.
"""

import logging
import re
from typing import Callable, Optional

import requests

from raider.plugins.common import Plugin


class Regex(Plugin):
    """Plugin class to extract regular expressions.

    This plugin will match the regex provided, and extract the ``value``
    inside the first matched group. A group is the string that matched
    inside the brackets.

    For example if the regular expression is:

    "accessToken":"([^"]+)"

    and the text to match it against contains:

    "accessToken":"0123456789abcdef"

    then only the string "0123456789abcdef" will be extracted and saved
    in the ``value`` attribute.

    Attributes:
      name:
        A string used as an identifier for the :class:`Regex`.
      regex:
        A string containing the regular expression to be matched.

    """

    def __init__(
        self,
        name: str,
        regex: str,
        function: Callable[[str], Optional[str]] = None,
        flags: int = Plugin.NEEDS_RESPONSE,
    ) -> None:
        """Initializes the Regex Plugin.

        Creates a Regex Plugin with the given regular expression, and
        extracts the matched group given in the "extract" argument, or
        the first matching group if not specified.

        Args:
          name:
            A string with the name of the Plugin.
          regex:
            A string containing the regular expression to be matched.
        """
        if not function:
            function = self.extract_regex_from_response
        super().__init__(
            name=name,
            function=function,
            flags=flags,
        )

        self.regex = regex

    def extract_regex_from_response(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Extracts regex from a HTTP response."""
        return self.extract_regex(response.text)

    def extract_regex_from_plugin(self) -> Optional[str]:
        """Extracts regex from a Plugin."""
        if self.plugins[0].value:
            return self.extract_regex(self.plugins[0].value)
        return None

    def extract_regex(self, text: str) -> Optional[str]:
        """Extracts defined regular expression from a text.

        Given a text to be searched for matches, return the string
        inside the group defined in "extract" or the first group if it's
        undefined.

        Args:
          text:
            A string containing the text to be searched for matches.

        Returns:
          A string with the match from the extracted group. Returns None
          if there are no matches.

        """
        matches = re.search(self.regex, text)
        if matches:
            groups = matches.groups()
            self.value = groups[0]
            logging.debug("Regex %s: %s", self.name, str(self.value))
        else:
            logging.warning(
                "Regex %s not found in the response body", self.name
            )

        return self.value

    @classmethod
    def from_plugin(cls, parent_plugin: Plugin, regex: str) -> "Regex":
        """Extracts Regex from another plugin's ``value``."""
        regex_plugin = cls(
            name=regex,
            regex=regex,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )
        regex_plugin.plugins = [parent_plugin]
        regex_plugin.function = regex_plugin.extract_regex_from_plugin
        return regex_plugin

    def __str__(self) -> str:
        """Returns a string representation of the Plugin."""
        return "Regex:" + self.regex
