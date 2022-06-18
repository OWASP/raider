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


"""Request class used to handle HTTP.
"""

import logging
import sys
import urllib
from copy import deepcopy
from typing import Any, Dict, List, Optional, Union

import requests
from urllib3.exceptions import InsecureRequestWarning

from raider.config import Config
from raider.plugins.basic import Cookie, File, Header
from raider.plugins.common import Plugin
from raider.structures import CookieStore, DataStore, HeaderStore
from raider.user import User


class PostBody(DataStore):
    """Holds the POST body data.

    This class was created to enable the user to send the POST body in a
    different format than the default url encoded. For now only JSON
    encoding has been implemented.

    Attributes:
      encoding:
        A string with the desired encoding. For now only "json" is
        supported. If the encoding is skipped, the request will be url
        encoded, and the Content-Type will be
        ``application/x-www-form-urlencoded``.

    """

    def __init__(self, data: Dict[Any, Any], encoding: str) -> None:
        """Initializes the PostBody object.

        Args:
          data:
            A dictionary with the data to be sent.
          encoding:
            A string with the encoding. Only "json" is supported for
            now.

        """
        self.encoding = encoding
        super().__init__(data)


def process_cookies(
    raw_cookies: CookieStore, userdata: Dict[str, str]
) -> Dict[str, str]:
    """Process the raw cookies and replace with the real data."""
    cookies = raw_cookies.to_dict().copy()
    for key in raw_cookies:
        name = raw_cookies[key].name
        if raw_cookies[key].name_not_known_in_advance:
            cookies.pop(key)
        value = raw_cookies[key].get_value(userdata)
        if value:
            cookies.update({name: value})
        else:
            cookies.pop(key)
    return cookies


def process_headers(
    raw_headers: HeaderStore, userdata: Dict[str, str], config: Config
) -> Dict[str, str]:
    """Process the raw headers and replace with the real data."""
    headers = raw_headers.to_dict().copy()
    headers.update({"user-agent": config.user_agent})
    for key in raw_headers:
        name = raw_headers[key].name
        if raw_headers[key].name_not_known_in_advance:
            headers.pop(key)
        value = raw_headers[key].get_value(userdata)
        if value:
            headers.update({name: value})
        else:
            headers.pop(name.lower())
    return headers


def process_data(
    raw_data: Union[PostBody, DataStore], userdata: Dict[str, str]
) -> Dict[str, str]:
    """Process the raw HTTP data and replace with the real data."""

    def traverse_dict(data: Dict[str, Any], userdata: Dict[str, str]) -> None:
        """Traverse a dictionary recursively and replace plugins
        with real data
        """
        for key in list(data):
            value = data[key]
            if isinstance(value, Plugin):
                new_value = value.get_value(userdata)
                if new_value:
                    data.update({key: new_value})
                else:
                    data.pop(key)
            elif isinstance(value, dict):
                traverse_dict(value, userdata)

            if isinstance(key, Plugin):
                new_value = data.pop(key)
                new_key = key.get_value(userdata)
                if new_key:
                    data.update({new_key: new_value})
                else:
                    data.pop(key)

    httpdata = raw_data.to_dict().copy()
    traverse_dict(httpdata, userdata)

    return httpdata


# Request needs many arguments
# pylint: disable=too-many-arguments
class Request:
    """Class holding the elements of the HTTP request.

    When a Flow object is created, it defines a Request object with
    the information necessary to create a HTTP request. The "method"
    and "url" attributes are required. Everything else is optional.

    The Request object can contain Plugins which will be evaluated and
    its value replaced in the HTTP request.

    Attributes:
      method:
        A string with the HTTP request method. Only GET and POST is
        supported for now.
      url:
        A string with the URL of the HTTP request.
      cookies:
        A list of Cookie objects to be sent with the HTTP request.
      headers:
        A list of Header objects to be sent with the HTTP request.
      data:
        A dictionary of Any objects. Can contain strings and
        Plugins. When a key or a value of the dictionary is a Plugin, it
        will be evaluated and its value will be used in the HTTP
        request. If the "method" is GET those values will be put inside
        the URL parameters, and if the "method" is POST they will be
        inside the POST request body.

    """

    def __init__(
        self,
        method: str,
        url: Optional[Union[str, Plugin]] = None,
        cookies: Optional[List[Cookie]] = None,
        headers: Optional[List[Header]] = None,
        data: Optional[Union[Dict[Any, Any], PostBody, File]] = None,
    ) -> None:
        """Initializes the Request object.

        Args:
          method:
            A string with the HTTP method. Can be either "GET" or "POST".
          url:
            A string with the full URL of the Request.
          cookies:
            A list of Cookie Plugins. Its values will be calculated and
            inserted into the HTTP Request on runtime.
          headers:
            A list of Header Plugins. Its values will be calculated and
            inserted into the HTTP Request on runtime.
          data:
            A dictionary with values to be inserted into the HTTP GET
            parameters or POST body. Both keys and values of the
            dictionary can be Plugins. Those values will be inserted
            into the Request on runtime.

        """
        self.method = method
        if not self.method:
            logging.critical("Required :method parameter, can't run without")

        if not url:
            logging.critical("Required :url parameter, can't run without")
            sys.exit()

        self.url = url

        self.headers = HeaderStore(headers)
        self.cookies = CookieStore(cookies)

        self.data: Union[PostBody, DataStore]
        if isinstance(data, PostBody):
            self.data = data
        elif isinstance(data, File):
            self.data = data
        else:
            self.data = DataStore(data)

    def list_inputs(self) -> Optional[Dict[str, Plugin]]:
        """Returns a list of request's inputs."""

        def get_children_plugins(plugin: Plugin) -> Dict[str, Plugin]:
            """Returns the children plugins.

            If a plugin has the flag DEPENDS_ON_OTHER_PLUGINS set,
            return a dictionary with each plugin associated to its name.

            """
            output = {}
            if plugin.depends_on_other_plugins:
                for item in plugin.plugins:
                    output.update({item.name: item})
            return output

        inputs = {}

        if isinstance(self.url, Plugin):
            inputs.update({self.url.name: self.url})
            inputs.update(get_children_plugins(self.url))

        for name in self.cookies:
            cookie = self.cookies[name]
            inputs.update({name: cookie})
            inputs.update(get_children_plugins(cookie))

        for name in self.headers:
            header = self.headers[name]
            inputs.update({name: header})
            inputs.update(get_children_plugins(header))

        for key, value in self.data.items():
            if isinstance(key, Plugin):
                inputs.update({key.name: key})
                inputs.update(get_children_plugins(key))
            if isinstance(value, Plugin):
                inputs.update({value.name: value})
                inputs.update(get_children_plugins(value))

        return inputs

    def process_inputs(
        self, user: User, config: Config
    ) -> Dict[str, Dict[str, str]]:
        """Process the Request inputs.

        Uses the supplied user data to replace the Plugins in the inputs
        with their actual value. Returns those values.

        Args:
          user:
            A User object containing the user specific data to be used
            when processing the inputs.
          config:
            A Config object with the global Raider configuration.

        Returns:
          A dictionary with the cookies, headers, and other data created
          from processing the inputs.

        """

        userdata = user.to_dict()

        if isinstance(self.url, Plugin):
            self.url = self.url.get_value(userdata)

        cookies = process_cookies(self.cookies, userdata)
        headers = process_headers(self.headers, userdata, config)
        if isinstance(self.data, File):
            httpdata = self.data.get_value(userdata)
        else:
            httpdata = process_data(self.data, userdata)

        return {"cookies": cookies, "data": httpdata, "headers": headers}

    def send(
        self, user: User, config: Config
    ) -> Optional[requests.models.Response]:
        """Sends the HTTP request.

        With the given user information, replaces the input plugins with
        their values, and sends the HTTP request. Returns the response.

        Args:
          user:
            A User object with the user specific data to be used when
            processing inputs.
          config:
            A Config object with the global Raider configuration.

        Returns:
          A requests.models.Response object with the HTTP response
          received after sending the generated request.

        """
        verify = config.verify
        if not verify:
            # False positive
            # pylint: disable=no-member
            requests.packages.urllib3.disable_warnings(
                category=InsecureRequestWarning
            )

        proxies = {"all": config.proxy}

        inputs = self.process_inputs(user, config)
        cookies = inputs["cookies"]
        headers = inputs["headers"]
        data = inputs["data"]

        logging.debug("Sending HTTP request:")
        logging.debug("%s %s", self.method, self.url)
        logging.debug("Cookies: %s", str(cookies))
        logging.debug("Headers: %s", str(headers))
        logging.debug("Data: %s", str(data))

        if self.method == "GET":
            # Encode special characters. This will replace "+" signs with "%20"
            # in URLs. For some reason mypy doesn't like this, so typing will
            # be ignored for this line.
            params = urllib.parse.urlencode(
                data, quote_via=urllib.parse.quote
            )  # type: ignore
            req = requests.get(
                self.url,
                params=params,
                headers=headers,
                cookies=cookies,
                proxies=proxies,
                verify=verify,
                allow_redirects=False,
            )

            return req

        if self.method == "POST":
            if (
                isinstance(self.data, PostBody)
                and self.data.encoding == "json"
            ):
                req = requests.post(
                    self.url,
                    json=data,
                    headers=headers,
                    cookies=cookies,
                    proxies=proxies,
                    verify=verify,
                    allow_redirects=False,
                )
            else:
                req = requests.post(
                    self.url,
                    data=data,
                    headers=headers,
                    cookies=cookies,
                    proxies=proxies,
                    verify=verify,
                    allow_redirects=False,
                )
            return req

        if self.method == "PATCH":
            if (
                isinstance(self.data, PostBody)
                and self.data.encoding == "json"
            ):
                req = requests.patch(
                    self.url,
                    json=data,
                    headers=headers,
                    cookies=cookies,
                    proxies=proxies,
                    verify=verify,
                    allow_redirects=False,
                )
            else:
                req = requests.patch(
                    self.url,
                    data=data,
                    headers=headers,
                    cookies=cookies,
                    proxies=proxies,
                    verify=verify,
                    allow_redirects=False,
                )
            return req

        if self.method == "PUT":
            req = requests.put(
                self.url,
                data=data,
                headers=headers,
                cookies=cookies,
                proxies=proxies,
                verify=verify,
                allow_redirects=False,
            )

            return req

        logging.critical("Method %s not allowed", self.method)
        sys.exit()
        return None


class Template(Request):
    """Template class to hold requests.

    It will initiate itself with a :class:`Request
    <raider.request.Request>` parent, and when called will return a
    copy of itself with the modified parameters.

    """

    def __init__(
        self,
        method: str,
        url: Optional[Union[str, Plugin]] = None,
        cookies: Optional[List[Cookie]] = None,
        headers: Optional[List[Header]] = None,
        data: Optional[Union[Dict[Any, Any], PostBody]] = None,
    ) -> None:
        """Initializes the template object."""
        super().__init__(
            method=method,
            url=url,
            cookies=cookies,
            headers=headers,
            data=data,
        )

    def __call__(
        self,
        method: Optional[str] = None,
        url: Optional[Union[str, Plugin]] = None,
        cookies: Optional[List[Cookie]] = None,
        headers: Optional[List[Header]] = None,
        data: Optional[Union[Dict[Any, Any], PostBody]] = None,
    ) -> "Template":
        """Allow the object to be called.

        Accepts the same arguments as the :class:`Request
        <raider.request.Request>` class. When called, will return a copy
        of itself with the modified parameters.

        """
        template = deepcopy(self)

        if method:
            template.method = method

        if url:
            template.url = url

        if cookies:
            template.cookies.merge(CookieStore(cookies))

        if headers:
            template.headers.merge(HeaderStore(headers))

        if data:
            if isinstance(data, PostBody):
                template.data.update(data.to_dict())
            else:
                template.data.update(data)

        return template
