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


from raider.config import Config
from raider.flow import Flow


class FlowGraph:
    def __init__(self, start: Flow, test: Flow = None) -> None:
        """Initializes the FlowGraph object."""
        self.start = start
        self.test = test
        self.completed = False
