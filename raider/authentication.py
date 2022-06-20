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

"""Authentication class responsible for running the defined stages.
"""

import logging
import sys
from typing import Dict, Optional, Union

from raider.config import Config
from raider.flow import AuthFlow, Flow
from raider.plugins.basic import Cookie, Header, Html, Json, Regex
from raider.user import User


class Authentication:
    """Class holding authentication stages.

    This class holds all the information necessary to authenticate. It
    provides functions to run those authentication steps.

    Attributes:
      stages:
        A list of Flow objects relevant to the authentication process.

    """

    def __init__(self, stages: Dict[str, AuthFlow]) -> None:
        """Initializes the Authentication object.

        Creates an object to handle the authentication process.

        Args:
          stages:
            A list of Flow objects defined inside "_authentication"
            variable in hy configuration files.

        """
        self.stages = stages
        self._current_stage = 0

    def __getitem__(self, key: str) -> Optional[AuthFlow]:
        if key not in self.stages.keys():
            return None
        return self.stages[key]

    def get_stage_name_by_id(self, stage_id: int) -> str:
        """Returns the stage name given its number.

        Each authentication step is given an index based on its position
        in the "_authentication" list. This function returns the name of
        the Flow based on its position in this list.

        Args:
          stage_id:
            An integer with the index of the stage.

        Returns:
          A string with the name of the Flow in the position "stage_id".

        """
        return list(self.stages.keys())[stage_id]

    def get_stage_index(self, name: str) -> int:
        """Returns the index of the stage given its name.


        Each authentication step is given an index based on its position
        in the "_authentication" list. This function returns the index of
        the Flow based on its name.

        Args:
          name:
            A string with the name of the Flow.

        Returns:
          An integer with the index of the Flow with the specified "name".
        """
        keys = list(self.stages.keys())

        if not name or name not in keys:
            return -1

        return keys.index(name)

    def run_all(self, user: User, config: Config) -> None:
        """Runs all authentication stages.

        This function will run all authentication stages for the
        specified User and will take into account the supplied Config
        for things like the user agent and the web proxy to use.

        Args:
          user:
            A User object containing the credentials and where the user
            specific data will be stored.
          config:
            A Config object with the global Raider settings.

        """
        while self._current_stage >= 0:
            self.run_current_stage(user, config)

        self._current_stage = 0

    def run_current_stage(self, user: User, config: Config) -> None:
        """Runs the current stage only.

        Authentication class keeps the index of the current stage in the
        "_current_stage" variable. This function runs only one
        authentication step indexed by this variable.

        Args:
          user:
            A User object containing the credentials and where the user
            specific data will be stored.
          config:
            A Config object with the global Raider settings.

        """
        logging.info(
            "Running stage %s",
            self.get_stage_name_by_id(self._current_stage),
        )
        self.run_stage(self._current_stage, user, config)

    def run_stage(
        self, stage_id: Union[int, str], user: User, config: Config
    ) -> Optional[str]:
        """Runs one authentication Stage.

        First, the Flow object of the specified stage is identified,
        then the related HTTP request is processed, sent, the response
        is received, and the operations are run on the Flow.

        Args:
          stage_id:
            A string or an integer identifying the authentication stage
            to run. If it's a string, it's the name of the Flow, and if
            it's an integer, it's the index of the Flow object in the
            "_authentication" variable.
          user:
            A User object containing the credentials and where the user
            specific data will be stored.
          config:
            A Config object with the global Raider settings.

        Returns:
          Optionally, this function returns a string with the name of
          the next Flow in the authentication process.

        """

        stage: Optional[Flow]
        if isinstance(stage_id, int):
            stage_name = self.get_stage_name_by_id(stage_id)
            stage = self.stages[stage_name]
        elif isinstance(stage_id, str):
            stage = self.stages[stage_id]

        if not stage:
            logging.critical("Stage %s not defined. Cannot continue", stage_id)
            sys.exit()

        stage.execute(user, config)

        if stage.outputs:
            for item in stage.outputs:
                if isinstance(item, Cookie):
                    user.set_cookie(item)
                elif isinstance(item, Header):
                    user.set_header(item)
                elif isinstance(item, (Regex, Html, Json)):
                    user.set_data(item)

        next_stage = stage.run_operations()
        if next_stage:
            self._current_stage = self.get_stage_index(next_stage)
        else:
            self._current_stage = -1
        return next_stage

    @property
    def current_stage_name(self) -> str:
        """Returns the name of the current stage."""
        return self.get_stage_name_by_id(self._current_stage)
