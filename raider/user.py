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

"""Classes used for handling users.
"""


from typing import Dict, List

import hy

from raider.plugins.basic.cookie import Cookie
from raider.plugins.basic.header import Header
from raider.plugins.common import Plugin
from raider.structures import CookieStore, DataStore, HeaderStore
from raider.utils import hy_dict_to_python


class User:
    """Class holding user related information.

    :class:`User` objects are created inside the :class:`Users`. Each
    :class:`User` object contains at least the ``username`` and the
    ``password``. Every time a :class:`Plugin
    <raider.plugins.common.Plugin>` generates an output, it is saved
    in the :class:`User` object. If the :class:`Plugin
    <raider.plugins.common.Plugin>` is a :class:`Cookie
    <raider.plugins.basic.Cookie>` or a :class:`Header
    <raider.plugins.basic.Header>`, the output will be stored in the
    the ``cookies`` and ``headers`` attributes respectively. Otherwise
    they'll be saved inside ``data``.

    Attributes:
      username:
        A string containing the user's email or username used to log in.
      password:
        A string containing the user's password.
      cookies:
        A :class:`CookieStore <raider.structures.CookieStore>` object
        containing all of the collected cookies for this user. The
        :class:`Cookie <raider.plugins.basic.Cookie>` plugin only
        writes here.
      headers:
        A :class:`HeaderStore <raider.structures.HeaderStore>` object
        containing all of the collected headers for this user. The
        :class:`Header <raider.plugins.basic.Header>` plugin only
        writes here.
      data:
        A :class:`DataStore <raider.structures.DataStore>` object
        containing the rest of the data collected from plugins for
        this user.

    """

    def __init__(
        self,
        username: str = None,
        password: str = None,
        **kwargs: Dict[str, str],
    ) -> None:
        """Initializes a :class:`User` object.

        Creates an object for easy access to user specific
        information. It's used to store the ``username``,
        ``password``, ``cookies``, ``headers``, and other ``data``
        extracted from the :class:`Plugin
        <raider.plugins.common.Plugin>` objects.

        Args:
          username:
            A string with the username used for the login process.
          password:
            A string with the password used for the login process.
          **kwargs:
            A dictionary with additional data about the user.

        """

        self.username = username
        self.password = password

        self.cookies = CookieStore.from_dict(kwargs.get("cookies"))
        self.headers = HeaderStore.from_dict(kwargs.get("headers"))
        self.data = DataStore(kwargs.get("data"))

    def set_cookie(self, cookie: Cookie) -> None:
        """Sets the ``cookies`` for the user.

        Given a :class:`Cookie <raider.plugins.basic.Cookie>` object,
        update the user's ``cookies`` attribute to include this
        :class:`Cookie's <raider.plugins.basic.Cookie>` value.

        Args:
          cookie:
            A :class:`Cookie <raider.plugins.basic.Cookie>`
            :class:`Plugin <raider.plugins.common.Plugin>` object with
            the data to be added.

        """
        if cookie.value:
            self.cookies.set(cookie)

    def set_cookies_from_dict(self, data: Dict[str, str]) -> None:
        """Set user's ``cookies`` from a dictionary.

        Given a dictionary of cookie values as strings, convert them
        to :class:`Cookie <raider.plugins.Cookie>` objects, and load
        them in the :class:`User <raider.user.User>` object
        respectively.

        Args:
          data:
            A dictionary of strings corresponding to cookie keys and
            values.

        """
        cookies = []
        for key, value in data.items():
            cookie = Cookie(key, value)
            cookies.append(cookie)

        for item in cookies:
            self.set_cookie(item)

    def set_header(self, header: Header) -> None:
        """Sets the ``headers`` for the user.

        Given a :class:`Header <raider.plugins.basic.Header>` object,
        update the user's ``headers`` attribute to include this header
        value.

        Args:
          header:
            A :class:`Header <raider.plugins.basic.Header>`
            :class:`Plugin <raider.plugins.common.Plugin` object with
            the data to be added.

        """
        if header.value:
            self.headers.set(header)

    def set_headers_from_dict(self, data: Dict[str, str]) -> None:
        """Set user's ``headers`` from a dictionary.

        Given a dictionary of header values as strings, convert them
        to :class:`Header <raider.plugins.Header>` objects, and load
        them in the :class:`User <raider.user.User>` object
        respectively.

        Args:
          data:
            A dictionary of strings corresponding to header keys and
            values.

        """
        headers = []
        for key, value in data.items():
            header = Header(key, value)
            headers.append(header)

        for item in headers:
            self.set_header(item)

    def set_data(self, data: Plugin) -> None:
        """Sets the ``data`` for the user.

        Given a :class:`Plugin <raider.plugins.common.Plugin>`, update
        the user's ``data`` attribute to include this data.

        Args:
          data:
            A :class:`Plugin <raider.plugins.common.Plugin>` object
            with the data to be added.

        """
        if data.value:
            self.data.update({data.name: data.value})

    def set_data_from_dict(self, data: Dict[str, str]) -> None:
        """Set user's ``data`` from a dictionary.

        Given a dictionary of data items made out of strings, update
        the ``data`` attribute accordingly.

        Args:
          data:
            A dictionary of strings corresponding to data keys and
            values.

        """
        for key, value in data.items():
            self.data.update({key: value})

    def to_dict(self) -> Dict[str, str]:
        """Returns this object's data in a dictionary format."""
        data = {}
        data["username"] = self.username
        data["password"] = self.password
        data.update(self.cookies.to_dict())
        data.update(self.headers.to_dict())
        data.update(self.data.to_dict())
        return data


class Users(DataStore):
    """Class holding all the users of the application.

    Users inherits from :class:`DataStructure
    <raider.structures.DataStore>`, and contains the users set up in
    :term:`hyfiles`. Each user is an :class:`User` object. The data
    from a :class:`Users` object can be accessed same way like from
    the :class:`DataStore <raider.structures.DataStore>`.

    Attributes:
      active_user:
        A string with the ``username`` attribute of the currently
        active :class:`User`.
    """

    def __init__(
        self,
        users: List[Dict[hy.models.Keyword, str]] = None,
        active_user: str = "DEFAULT",
    ) -> None:
        """Initializes the :class:`Users` object.

        Given a `list
        <https://docs.hylang.org/en/stable/syntax.html#hy.models.List>`_
        of `dictionaries
        <https://docs.hylang.org/en/stable/syntax.html#dictionary-literals>`_,
        map them to a :class:`User` object and store them in this
        :class:`Users` object.

        Args:
          users:
            A list of dictionaries. Dictionary's data is mapped to a
            :class:`User` object.
          active_user:
            An optional string specifying the default :class:`User`.

        """
        if users:
            self.active_user = list(users[0].keys())[0]
        else:
            self.active_user = active_user

        values = {}
        if users:
            for item in users:
                username = list(item.keys())[0]
                password = item[username]
                item.pop(username)
                user = User(
                    username, password, **{"data": hy_dict_to_python(item)}
                )
                values[username] = user
        else:
            username = "DEFAULT"
            password = ""
            user = User(username, password)
            values[username] = user

        super().__init__(values)

    def to_dict(self) -> Dict[str, str]:
        """Returns the :class:`Users` object data in dictionary format."""
        data = {}
        for username in self:
            data[username] = self[username].to_dict()

        return data

    @property
    def active(self) -> User:
        """Returns the active :class:`User` as an :class:`Users` object."""
        return self[self.active_user]
