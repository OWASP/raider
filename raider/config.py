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

"""Config class holding global Raider configuration.
"""

import logging
import os
import sys
from typing import Any, Dict

from raider.logger import get_logger
from raider.utils import (
    create_hy_expression,
    default_user_agent,
    eval_file,
    eval_project_file,
    get_config_file,
    get_project_dir,
    list_hyfiles,
    list_projects,
)


class Config:
    """Class dealing with global Raider configuration.

    A Config object will contain all the information necessary to run
    Raider. It will define global configurations like the web proxy and
    the logging level, but also the data defined in the active project
    configuration files.

    Attributes:
      proxy:
        An optional string to define the web proxy to relay the traffic
        through.
      verify:
        A boolean flag which will let the requests library know whether
        to check the SSL certificate or ignore it.
      loglevel:
        A string used by the logging library to define the desired
        logging level.
      user_agent:
        A string which will be used as the user agent in HTTP requests.
      active_project:
        A string defining the current active project.
      project_config:
        A dictionary containing all of the local variables defined in
        the active project's hy configuration files.
      logger:
        A logging.RootLogger object used for debugging.

    """

    def __init__(self) -> None:
        """Initializes the Config object.

        Retrieves configuration from "common.hy" file, or populates it
        with the default values if it doesn't exist.

        """
        filename = get_config_file("common.hy")
        if os.path.isfile(filename):
            output = eval_file(filename)
        else:
            output = {}

        self.output = output
        self.use_proxy = False

        self.logger = get_logger(self.loglevel, "raider")

    def write_config_file(self) -> None:
        """Writes global configuration to common.hy.

        Gets the current configuration from the Config object and writes
        them in hylang format in the "common.hy" file.
        """
        filename = get_config_file("common.hy")
        data = ""
        with open(filename, "w", encoding="utf-8") as conf_file:
            data += create_hy_expression("proxy", self.proxy)
            data += create_hy_expression("user_agent", self.user_agent)
            data += create_hy_expression("loglevel", self.loglevel)
            data += create_hy_expression("verify", self.verify)
            data += create_hy_expression("active_project", self.active_project)
            self.logger.debug("Writing to config file %s", filename)
            self.logger.debug("data = %s", str(data))
            conf_file.write(data)

    def print_config(self) -> None:
        """Prints current configuration."""
        print("proxy: " + str(self.proxy))
        print("verify: " + str(self.verify))
        print("loglevel: " + self.loglevel)
        print("user_agent: " + self.user_agent)
        print("active_project: " + str(self.active_project))

    @property
    def proxy(self):
        return self.output.get("proxy", None)

    @proxy.setter
    def proxy(self, value: str):
        self.output["proxy"] = value

    @property
    def verify(self):
        return self.output.get("verify", False)

    @verify.setter
    def verify(self, value: str):
        self.output["verify"] = value

    @property
    def loglevel(self):
        return self.output.get("loglevel", "WARNING")

    @loglevel.setter
    def loglevel(self, value: str):
        self.output["loglevel"] = value

    @property
    def user_agent(self):
        return self.output.get("user_agent", default_user_agent())

    @user_agent.setter
    def user_agent(self, value: str):
        self.output["user_agent"] = value

    @property
    def active_project(self):
        if self.output.get("active_project"):
            return self.output.get("active_project", None)
        if list_projects():
            return list_projects()[0]
        return None

    @active_project.setter
    def active_project(self, value: str):
        self.output["active_project"] = value
