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


"""Request class used to handle HTTP.
"""

import json
import logging
import sys
import urllib
from copy import deepcopy
from functools import partial
from typing import Any, Dict, List, Optional, Union

import requests
from urllib3.exceptions import InsecureRequestWarning

from raider.plugins.basic.cookie import Cookie
from raider.plugins.basic.file import File
from raider.plugins.basic.header import Header
from raider.plugins.common import Plugin
from raider.structures import CookieStore, DataStore, HeaderStore
from raider.user import User
from raider.utils import colors


def prompt_empty_key(element: str, name: str):
    key = input(
        colors["GREEN-BLACK-B"]
        + element
        + ' "'
        + colors["RED-BLACK-B"]
        + name
        + colors["GREEN-BLACK-B"]
        + '" has a value not known in advance. '
        + "Input its value manually (enter to skip)\n"
        + colors["YELLOW-BLACK-B"]
        + name
        + " = "
    )
    return key


def prompt_empty_value(element: str, name: str):
    value = input(
        colors["GREEN-BLACK-B"]
        + element
        + ' "'
        + colors["RED-BLACK-B"]
        + name
        + colors["GREEN-BLACK-B"]
        + '" has an empty value. '
        + "Input its value manually (enter to skip)\n"
        + colors["YELLOW-BLACK-B"]
        + name
        + " = "
    )
    return value


def get_empty_plugin_name(plugin):
    if isinstance(plugin, Cookie):
        return prompt_empty_value("Cookie name", plugin.name)
    elif isinstance(plugin, Header):
        return prompt_empty_value("Header name", plugin.name)
    else:
        return prompt_empty_value("Plugin name", plugin.name)


def get_empty_plugin_value(plugin, name):
    if isinstance(plugin, Cookie):
        return prompt_empty_value("Cookie", name)
    elif isinstance(plugin, Header):
        return prompt_empty_value("Header", name)
    else:
        return prompt_empty_value("Plugin", name)


def process_cookies(raw_cookies: CookieStore, pconfig) -> Dict[str, str]:
    """Process the raw cookies and replace with the real data."""
    cookies = raw_cookies.to_dict().copy()
    for key in raw_cookies:
        cookie = raw_cookies[key]
        if cookie.name_not_known_in_advance:
            cookies.pop(key)
        value = cookie.get_value(pconfig)
        if not value:
            if cookie.name_not_known_in_advance:
                cookie.name = get_empty_plugin_name(cookie)
                cookie.flags &= cookie.NAME_NOT_KNOWN_IN_ADVANCE
                cookie.flags |= cookie.NEEDS_USERDATA
                cookie.function = cookie.extract_value_from_userdata
            value = get_empty_plugin_value(cookie, cookie.name)
        if not value:
            cookies.pop(key)
        else:
            cookies.update({cookie.name: value})
    return cookies


def process_headers(raw_headers: HeaderStore, pconfig) -> Dict[str, str]:
    """Process the raw headers and replace with the real data."""
    headers = raw_headers.to_dict().copy()
    headers.update({"user-agent": pconfig.user_agent})
    for key in raw_headers:
        header = raw_headers[key]
        if header.name_not_known_in_advance:
            headers.pop(key)
        value = header.get_value(pconfig)
        if not value:
            if header.name_not_known_in_advance:
                header.name = get_empty_plugin_name(header)
                header.flags &= header.NAME_NOT_KNOWN_IN_ADVANCE
                header.flags |= header.NEEDS_USERDATA
                header.function = header.extract_value_from_userdata
            value = get_empty_plugin_value(header, header.name)
        if not value:
            headers.pop(header.name.lower())
        else:
            headers.update({header.name: value})
    return headers


def process_data(raw_data: Dict[str, DataStore], pconfig) -> Dict[str, str]:
    """Process the raw HTTP data and replace with the real data."""

    def traverse_dict(data: Dict[str, Any], pconfig) -> None:
        """Traverse a dictionary recursively and replace plugins
        with real data
        """
        for key in list(data):
            value = data[key]
            if isinstance(value, Plugin):
                new_value = value.get_value(pconfig)
                if not new_value:
                    new_value = get_empty_plugin_value(value, value.name)
                if not new_value:
                    data.pop(key)
                else:
                    data.update({key: new_value})
            elif isinstance(value, dict):
                traverse_dict(value, pconfig)

            if isinstance(key, Plugin):
                new_value = data.pop(key)
                new_key = key.get_value(pconfig)
                if not new_key:
                    new_key = get_empty_plugin_value(key, key.name)
                if not new_key and key in data:
                    data.pop(key)
                else:
                    data.update({new_key: new_value})

    httpdata = {}
    for key, value in raw_data.items():
        if isinstance(value, File):
            httpdata[key] = value.get_value(pconfig)
        else:
            new_dict = value.to_dict().copy()
            traverse_dict(new_dict, pconfig)
            httpdata[key] = new_dict

    return httpdata


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

    def __init__(self, function, url: str, method: str, **kwargs) -> None:
        """Initializes the Request object."""
        self.method = method
        self.function = function
        self.url = url

        self.logger = None
        self.headers = HeaderStore(kwargs.get("headers"))
        self.cookies = CookieStore(kwargs.get("cookies"))
        self.kwargs = kwargs

        data = {}
        for key, value in kwargs.items():
            if key in ["params", "data", "json", "multipart"]:
                if isinstance(value, File):
                    data[key] = value
                else:
                    data[key] = DataStore(value)
        self.data = data

    @classmethod
    def get(cls, url, **kwargs) -> "Request":
        return cls(function=requests.get, url=url, method="GET", **kwargs)

    @classmethod
    def post(cls, url, **kwargs) -> "Request":
        return cls(function=requests.post, url=url, method="POST", **kwargs)

    @classmethod
    def put(cls, url, **kwargs) -> "Request":
        return cls(function=requests.put, url=url, method="PUT", **kwargs)

    @classmethod
    def patch(cls, url, **kwargs) -> "Request":
        return cls(function=requests.patch, url=url, method="PATCH", **kwargs)

    @classmethod
    def head(cls, url, **kwargs) -> "Request":
        return cls(function=requests.head, url=url, method="HEAD", **kwargs)

    @classmethod
    def delete(cls, url, **kwargs) -> "Request":
        return cls(
            function=requests.delete, url=url, method="DELETE", **kwargs
        )

    @classmethod
    def connect(cls, url, **kwargs) -> "Request":
        function = partial(requests.request, method="CONNECT")
        return cls(function=function, url=url, method="CONNECT", **kwargs)

    @classmethod
    def options(cls, url, **kwargs) -> "Request":
        return cls(
            function=requests.options, url=url, method="OPTIONS", **kwargs
        )

    @classmethod
    def trace(cls, url, **kwargs) -> "Request":
        function = partial(requests.request, method="TRACE")
        return cls(function=function, url=url, method="TRACE", **kwargs)

    @classmethod
    def custom(cls, method, url, **kwargs) -> "Request":
        function = partial(requests.request, method=method)
        return cls(function=function, url=url, method=method, **kwargs)

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

    def send(self, pconfig) -> Optional[requests.models.Response]:
        """Sends the HTTP request.

        With the given user information, replaces the input plugins with
        their values, and sends the HTTP request. Returns the response.

        Args:
          user:
            A User object with the user specific data to be used when
            processing inputs.
          pconfig:
            A Config object with the global Raider configuration.

        Returns:
          A requests.models.Response object with the HTTP response
          received after sending the generated request.

        """
        verify = pconfig.verify

        self.logger = pconfig.logger
        if not verify:
            # False positive
            # pylint: disable=no-member
            requests.packages.urllib3.disable_warnings(
                category=InsecureRequestWarning
            )

        if pconfig.use_proxy:
            proxies = {"all": pconfig.proxy}
        else:
            proxies = None

        if isinstance(self.url, Plugin):
            url = self.url.get_value(pconfig)
        else:
            url = self.url

        cookies = process_cookies(self.cookies, pconfig)
        headers = process_headers(self.headers, pconfig)
        processed = process_data(self.data, pconfig)
        pconfig.active_user.set_cookies_from_dict(cookies)
        pconfig.active_user.set_headers_from_dict(headers)
        pconfig.active_user.set_data_from_dict(processed)

        # Encode special characters. This will replace "+" signs with "%20"
        if "params" in self.kwargs:
            params = urllib.parse.urlencode(
                processed["params"], quote_via=urllib.parse.quote
            )
        else:
            params = None

        if self.kwargs.get("json"):
            if isinstance(processed["json"], str):
                json_data = json.loads(processed["json"])
            else:
                json_data = processed["json"]
        else:
            json_data = None

        self.logger.debug("Sending HTTP request:")
        self.logger.debug("%s %s", self.method, url)
        self.logger.debug("Cookies: %s", str(cookies))
        self.logger.debug("Headers: %s", str(headers))
        self.logger.debug("Params: %s", str(params))
        self.logger.debug("Data: %s", str(processed.get("data")))
        self.logger.debug("JSON: %s", str(processed.get("json")))
        self.logger.debug("Multipart: %s", str(processed.get("multipart")))

        try:
            req = self.function(
                url=url,
                headers=headers,
                cookies=cookies,
                proxies=proxies,
                verify=verify,
                allow_redirects=False,
                params=params,
                data=processed.get("data"),
                json=json_data,
                files=processed.get("multipart"),
            )
        except requests.exceptions.ProxyError:
            self.logger.critical("Cannot establish connection!")
            sys.exit()

        return req


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
        data: Optional[Union[Dict[Any, Any]]] = None,
    ) -> None:
        """Initializes the template object."""
        function = partial(requests.request, method=method)
        super().__init__(
            function=function,
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
        data: Optional[Union[Dict[Any, Any]]] = None,
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
            template.data.update(data)

        return template
