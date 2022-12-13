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

"""Plugins used to process data.
"""

import base64
import urllib
from typing import Optional, Union

from raider.plugins.common import Plugin, Processor


class Urlencode(Processor):
    """URL Encode the plugin."""

    def __init__(self, parent_plugin: Plugin) -> None:
        """Initializes the Urlencode plugin."""
        super().__init__(
            name=parent_plugin.name + "_urlencoded", function=self.urlencode
        )
        self.plugins = [parent_plugin]

    def urlencode(self) -> str:
        """URL encodes a plugin's value."""

        original = self.plugins[0].value
        encoded = urllib.parse.quote(original)
        return encoded


class Urldecode(Processor):
    """URL Decode the plugin."""

    def __init__(self, parent_plugin: Plugin) -> None:
        """Initializes the Urldecode plugin."""
        super().__init__(
            name=parent_plugin.name + "_urldecoded", function=self.urldecode
        )
        self.plugins = [parent_plugin]

    def urldecode(self) -> Optional[str]:
        """URL decodes a plugin's value."""

        original = self.plugins[0].value
        if original:
            decoded = urllib.parse.unquote(original)
            return decoded
        return None


class B64decode(Processor):
    """Base64 Decode the plugin."""

    def __init__(self, parent_plugin: Plugin) -> None:
        """Initializes the B64decode plugin."""
        super().__init__(
            name=parent_plugin.name + "_b64decoded", function=self.b64decode
        )
        self.plugins = [parent_plugin]

    def b64decode(self) -> Optional[str]:
        """Base64 decodes a plugin's value."""

        original = self.plugins[0].value
        if original:
            decoded = base64.b64decode(original).decode("utf-8")
            return decoded
        return None


class B64encode(Processor):
    """Base64 encode the plugin."""

    def __init__(self, original: Union[Plugin, str]) -> None:
        """Initializes the B64encode plugin."""
        if isinstance(original, Plugin):
            super().__init__(
                name=original.name + "_b64encoded", function=self.b64encode
            )
            self.plugins = [original]
        else:
            super().__init__(
                name=original + "_b64encoded", function=self.b64encode
            )
            self.original = original

    def b64encode(self) -> Optional[str]:
        """Base64 encodes a value."""

        if self.plugins:
            original = self.plugins[0].value
        else:
            original = self.original

        if original:
            encoded = base64.b64encode(original.encode("utf-8")).decode(
                "utf-8"
            )
            return encoded
        return None
