.. _prerequisites:

Prerequisites
=============

Learn Python basics
-------------------

You should know enough `Python <https://www.python.org>`_
to be able to write and debug short scripts. Get comfortable reading
documentations for the things you don't know. You need to have an
understanding of Python concepts in order to learn Hylang, which is
essential if you want to use Raider.

Learn Hylang basics
-------------------

Raider's configuration files are written in `Hylang
<https://docs.hylang.org/en/stable>`_, a LISP dialect on top of
Python. You can't really use Raider if you skip this step. But you
also don't need a lot to start using Raider. You just have to learn to
accept the LISP paranthesis and write simple scripts like you should
already be able to do with Python. If you're already familiar with
LISP and Python, this step will be easy for you.

Resources
+++++++++

* `Hylang Tutorial <https://docs.hylang.org/en/stable/tutorial.html>`_


Get comfortable with a web proxy
--------------------------------

Pick up a web proxy you like, and learn how to use it properly. We
recommend `BurpSuite <https://portswigger.net/burp>`_, `ZAProxy
<https://www.zaproxy.org/>`_ or `mitmproxy
<https://mitmproxy.org/>`_. You will need this to reverse engineer the
HTTP processes for arbitrary web applications.


Resources
+++++++++

* `Burpsuite Homepage <https://portswigger.net/burp>`_
* `Burpsuite Tutorial Video by John Hammond <https://www.youtube.com/watch?v=G3hpAeoZ4ek>`_


Learn the basics of authentication
----------------------------------

Now that you already know how to use a web proxy, you should learn how
the authentication works on web applications. Log into different
websites while using the web proxy, and try to understand how it
works, i.e. what information is being sent to the server, what does
the server responds with, and where each piece of information comes
from. Try first with simple websites, and gradually move to more
complicated until you understand the process.



