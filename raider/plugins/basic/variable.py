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
"""Variable Plugin to extract user data.
"""

from raider.plugins.common import Plugin


class Variable(Plugin):
    """:class:`Plugin <raider.plugins.common.Plugin>` to extract data
    from the :class:`User <raider.user.User>`

    Use this when the ``value`` of the plugin should be extracted from
    the user data. ``username`` and ``password`` are mandatory and can
    be accessed with ``(Variable "username")`` and ``(Variable
    "password")`` respectively. Other data can be accessed similarly.

    Attributes:
      name:
        A string used as an identifier for the :class:`Variable`
        :class:`Plugin <raider.plugins.common.Plugin>`

    """

    def __init__(self, name: str) -> None:
        """Initializes the :class:`Variable` :class:`Plugin
        <raider.plugins.common.Plugin>`.

        Creates a :class:`Variable` object that will return the data
        from the :class:`User <raider.user.User>` object.

        Args:
          name:
            A String with the name of the variable.

        """
        super().__init__(
            name=name,
            function=lambda data: data[self.name],
            flags=Plugin.NEEDS_USERDATA,
        )
