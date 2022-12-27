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
"""Plugin to work with JSON data.
"""

import json
import logging
from typing import Callable, Optional

import requests

from raider.plugins.common import Plugin
from raider.utils import parse_json_filter


class Json(Plugin):
    """

    The "extract" attribute is used to specify which field to store in
    the ``value``. Using the dot ``.`` character you can go deeper inside
    the JSON object. To look inside an array, use square brackets
    `[]`.

    Keys with special characters should be written inside double quotes
    ``"``. Keep in mind that when written inside ``hyfiles``,
    it'll already be between double quotes, so you'll have to escape
    them with the backslash character ``\\``.

    Examples:

      ``env.production[0].field``
      ``production.keys[1].x5c[0][1][0]."with space"[3]``

    Attributes:
      extract:
        A string defining the location of the field that needs to be
        extracted. For now this is still quite primitive, and cannot
        access data from JSON arrays.

    """

    def __init__(
        self,
        name: str,
        extract: str,
        function: Callable[[str], Optional[str]] = None,
        flags: int = Plugin.NEEDS_RESPONSE,
    ) -> None:
        """Initializes the Json Plugin.

        Creates the Json Plugin and extracts the specified field.

        Args:
          name:
            A string with the name of the Plugin.
          extract:
            A string with the location of the JSON field to extract.
        """
        if not function:
            function = self.extract_json_from_response
        super().__init__(
            name=name,
            function=function,
            flags=flags,
        )

        self.extract = extract

    def extract_json_from_response(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Extracts the json field from a HTTP response."""
        return self.extract_json_field(response.text)

    def extract_json_from_plugin(self) -> Optional[str]:
        """Extracts the json field from a plugin."""
        if self.plugins[0].value:
            return self.extract_json_field(self.plugins[0].value)
        return None

    def extract_json_field(self, text: str) -> Optional[str]:
        """Extracts the JSON field from the text.

        Given the JSON body as a string, extract the field and store it
        in the Plugin's ``value`` attribute.

        Args:
          text:
            A string with the JSON body.

        Returns:
          A string with the result of extraction. If no such field is
          found None will be returned.

        """
        try:
            data = json.loads(text)
        except json.decoder.JSONDecodeError:
            return None

        json_filter = parse_json_filter(self.extract)
        is_valid = True
        temp = data
        for item in json_filter:
            if item.startswith("["):
                index = int(item.strip("[]"))
                if len(temp) > index:
                    temp = temp[index]
                else:
                    logging.warning(
                        (
                            "JSON array index doesn't exist.",
                            "Cannot extract plugin's value.",
                        )
                    )
                    is_valid = False
                    break
            else:
                if item in temp:
                    temp = temp[item]
                else:
                    logging.warning(
                        (
                            "Key '%s' not found in the response body.",
                            "Cannot extract plugin's value.",
                        ),
                        item,
                    )
                    is_valid = False
                    break

        if is_valid:
            self.value = str(temp)
            logging.debug("Json filter %s: %s", self.name, str(self.value))
        else:
            return None

        return self.value

    @classmethod
    def from_plugin(
        cls, parent_plugin: Plugin, name: str, extract: str
    ) -> "Json":
        """Extracts the JSON field from another plugin's ``value``."""
        json_plugin = cls(
            name=name,
            extract=extract,
            flags=Plugin.DEPENDS_ON_OTHER_PLUGINS,
        )
        json_plugin.plugins = [parent_plugin]
        json_plugin.function = json_plugin.extract_json_from_plugin
        return json_plugin

    def __str__(self) -> str:
        """Returns a string representation of the Plugin."""
        return "Json:" + str(self.extract)
