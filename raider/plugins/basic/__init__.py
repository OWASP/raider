"""Import basic plugins.
"""
from raider.plugins.basic.command import Command
from raider.plugins.basic.cookie import Cookie
from raider.plugins.basic.file import File
from raider.plugins.basic.header import Header
from raider.plugins.basic.html import Html
from raider.plugins.basic.jsonp import Json
from raider.plugins.basic.prompt import Prompt
from raider.plugins.basic.regex import Regex
from raider.plugins.basic.variable import Variable

__all__ = [
    "Command",
    "Cookie",
    "File",
    "Header",
    "Html",
    "Json",
    "Prompt",
    "Regex",
    "Variable",
]
