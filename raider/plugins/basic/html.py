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
"""Plugin to work with HTML tags
"""

import logging
from typing import Dict, Optional

import hy
import requests
from bs4 import BeautifulSoup

from raider.plugins.common import Plugin
from raider.utils import hy_dict_to_python, match_tag


class Html(Plugin):
    """

    This Plugin will find the HTML "tag" containing the specified
    "attributes" and store the "extract" attribute of the matched tag
    in its ``value`` attribute.

    Attributes:
      tag:
        A string defining the HTML tag to look for.
      attributes:
        A dictionary with attributes matching the desired HTML tag. The
        keys in the dictionary are strings matching the tag's attributes,
        and the ``value``s are treated as regular expressions, to help
        match tags that don't have a static ``value``.
      extract:
        A string defining the HTML tag's attribute that needs to be
        extracted and stored inside ``value``.
    """

    def __init__(
        self,
        name: str,
        tag: str,
        attributes: Dict[hy.models.Keyword, str],
        extract: str,
    ) -> None:
        """Initializes the Html Plugin.

        Creates a Html Plugin with the given "tag" and
        "attributes". Stores the "extract" attribute in the plugin's
        ``value``.

        Args:
          name:
            A string with the name of the Plugin.
          tag:
            A string with the HTML tag to look for.
          attributes:
            A hy dictionary with the attributes to look inside HTML
            tags. The ``value``s of dictionary elements are treated as
            regular expressions.
          extract:
            A string with the HTML tag attribute that needs to be
            extracted and stored in the Plugin's object.

        """
        super().__init__(
            name=name,
            function=self.extract_html_tag,
            flags=Plugin.NEEDS_RESPONSE,
        )
        self.tag = tag
        self.attributes = hy_dict_to_python(attributes)
        self.extract = extract

    def extract_html_tag(
        self, response: requests.models.Response
    ) -> Optional[str]:
        """Extract data from an HTML tag.

        Given the HTML text, parses it, iterates through the tags, and
        find the one matching the attributes. Then it stores the matched
        ``value`` and returns it.

        Args:
          text:
            A string containing the HTML text to be processed.

        Returns:
          A string with the match as defined in the Plugin. Returns None
          if there are no matches.

        """
        soup = BeautifulSoup(response.text, "html.parser")
        matches = soup.find_all(self.tag)

        for item in matches:
            if match_tag(item, self.attributes):
                if self.extract == "contents":
                    self.value = item.contents
                else:
                    self.value = item.attrs.get(self.extract)

        logging.debug("Html filter %s: %s", self.name, str(self.value))
        return self.value

    def __str__(self) -> str:
        """Returns a string representation of the Plugin."""
        return (
            "Html:"
            + self.tag
            + ":"
            + str(self.attributes)
            + ":"
            + str(self.extract)
        )
