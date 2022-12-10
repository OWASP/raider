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
"""Plugin to get input from the user.
"""

from raider.plugins.common import Plugin


class Prompt(Plugin):
    """:class:`Plugin <raider.plugins.common.Plugin>` to prompt the
    user for some data.

    Use this :class:`Plugin <raider.plugins.common.Plugin>` when the ``value``
    cannot be known in advance, for example when asking for
    :term:`multi-factor authentication (MFA)` code that is going to be
    sent over SMS or E-mail.

    Attributes:
      name:
        A String used both as an identifier for this :class:`Prompt`
        :class:`Plugin <raider.plugins.common.Plugin>` and as a prompt
        message on the terminal.

    """

    def __init__(self, name: str) -> None:
        """Initializes the :class:`Prompt` :class:`Plugin
        <raider.plugins.common.Plugin>`.

        Creates a :class:`Prompt` :class:`Plugin
        <raider.plugins.common.Plugin>` which will ask the user's
        input to get the :class:`Plugin's
        <raider.plugins.common.Plugin>` ``value``.

        Args:
          name:
            A String containing the prompt asking the user for input.

        """
        super().__init__(name=name, function=self.get_user_prompt)

    def get_user_prompt(self) -> str:
        """Gets the ``value`` from user input.

        Creates a prompt asking the user for input and stores the ``value``
        in the Plugin.

        Returns:
          A string with the input received from the user.

        """
        self.value = None
        print("Please provide the input value (enter to skip)")
        self.value = input(self.name + " = ")
        return self.value
