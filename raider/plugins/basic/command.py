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
"""Plugin to run arbitrary commands.
"""

import os
from typing import Optional

from raider.plugins.common import Plugin


class Command(Plugin):
    """

    Use this to run a shell command and extract the output.

    """

    def __init__(self, name: str, command: str) -> None:
        """Initializes the Command Plugin.

        The specified command will be executed with os.popen() and the
        output with the stripped last newline, will be saved inside the
        ``value``.

        Args:
          name:
            A unique identifier for the plugin.
          command:
            The command to be executed.

        """
        self.command = command
        super().__init__(
            name=name,
            function=self.run_command,
        )

    def run_command(self) -> Optional[str]:
        """Runs a command and returns its ``value``.

        Given a dictionary with the predefined variables, return the
        ``value`` of the with the same name as the "name" attribute from
        this Plugin.

        Args:
          data:
            A dictionary with the predefined variables.

        Returns:
          A string with the ``value`` of the variable found. None if no such
          variable has been defined.

        """
        self.value = os.popen(self.command).read().strip()

        return self.value
