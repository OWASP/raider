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

"""Functions class holding all Flows unrelated to authentication.
"""


import logging
import sys
from typing import Dict, Optional

from raider.config import Config
from raider.flow import Flow
from raider.user import User


class Functions:
    """Class holding all Flows that don't affect the authentication.

    This class shouldn't be used directly by the user, instead the
    Raider class should be used which will deal with Functions
    internally.

    Attributes:
      functions:
        A list of Flow objects with all available functions.

    """

    def __init__(self, functions: Dict[str, Flow]) -> None:
        """Initializes the Functions object.

        Args:
          functions:
            A list of Flow objects to be included in the Functions
            object.

        """
        self.functions = functions

    def __getitem__(self, key: str) -> Optional[Flow]:
        if key not in self.functions.keys():
            return None
        return self.functions[key]

    def get_flow_index(self, name: str) -> Optional[int]:
        """Returns the index of Flow in the Functions array."""
        keys = list(self.functions.keys())

        if not name or name not in keys:
            return -1

        return keys.index(name)

    def run_flow(self, name: str, user: User, config: Config) -> Optional[str]:
        """Runs a single Flow.

        Executes the given function, in the context of the specified
        user, and applies the global Raider configuration.

        Args:
          name:
            A string with the name of the function to run.
          user:
            A User object containing all the data needed to run the
            function in this user's context.
          config:
            A Config object with the global Raider configuration.

        """
        logging.info("Running function %s", name)
        function = self.functions[name]
        if function:
            function.execute(user, config)
            if function.outputs:
                for item in function.outputs:
                    if item.value:
                        user.set_data(item)

            next_stage = function.run_operations()
            return next_stage

        logging.critical("Function %s not defined. Cannot continue", name)
        sys.exit()

    def run_chain(self, name: str, user: User, config: Config) -> None:
        """Runs a Function, and follows the NextStage.

        Executes the given function, in the context of the specified
        user, and applies the global Raider configuration. Runs the next
        defined stage.


        Args:
          name:
            A string with the name of the function to run.
          user:
            A User object containing all the data needed to run the
            function in this user's context.
          config:
            A Config object with the global Raider configuration.

        """
        next_stage = name
        while next_stage:
            next_stage = self.run_flow(next_stage, user, config) or ""
