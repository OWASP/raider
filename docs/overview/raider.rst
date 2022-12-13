What is Raider
==============

.. image:: ../../ext/logo.png

**Raider** was initially designed to help test and automate web
:term:`authentication` processes, but by now has evolved and can be
used for all kinds of HTTP processess. Raider defines a `DSL
<https://en.wikipedia.org/wiki/Domain-specific_language>`_ to describe
the client-server information exchange of arbitrary complexity. It can
be infinitely extended since its configuration file is written in real
code and not just static files.

You can use it for example to create, store, reproduce, and share
proof-of-concepts easily for HTTP attacks. With Raider you can also
search through your Projects, filter by hyfile, Flows, FlowGraphs,
etc... Then you run either just one step, or a chain of steps, so you
can automate and run tests the HTTP process.


How does Raider work?
---------------------

**Raider** treats the HTTP process as a :term:`finite state
machine`. Each step is a different :term:`Flow`, with its own inputs
and outputs. Those can be cookies, headers, CSRF tokens, or other
pieces of information.

Each application needs its own configuration directory for **Raider**
to work. The configuration is written in `hylang
<https://docs.hylang.org/>`_. The language choice was done for
multiple reasons, mainly because it's a LISP dialect embedded in
Python.

:ref:`Using LISP was necessarily <why_lisp>` since sometimes the HTTP
processes can get quite complex, and using a static configuration file
would've not been enough to cover all the details. LISP makes it easy
to combine code and data, which is exactly what was needed here.

By using a real programming language as a configuration file gives
**Raider** a lot of power, and :ref:`with great power comes great
responsibility <faq_eval>`. Theoretically one can write entire malware
inside the application configuration file, which means you should be
careful what's being executed, and **not to use configuration files
from sources you don't trust**. **Raider** will evaluate everything
inside the ``.hy`` files, which means if you're not careful you could
shoot yourself in the foot and break something on your system.


Features
--------

Here are some of its most important features:

* A real programming language for configuration instead of a static file
* Infinitely extensible, easy to write custom operations and plugins
* Stateful HTTP process testing
* Manipulating inputs/outputs with real code
* Conditionally jump between steps
* Running arbitrary actions after receiving response


Raider's philosophy
-------------------

**Raider** is being developed with the following goals:

* To abstract HTTP information exchange using Python objects.
* To support most modern HTTP processes features.
* To make it easy to add new features for users.
  

And if you're looking at the code and willing to contribute, keep
those in mind:

* The simpler and cleaner the code, the better.
* New features should be implemented as :term:`Plugins <plugin>` and
  :term:`Operations <operation>` if possible.
* The :term:`hyfiles` should stay as minimal as possible, while still
  allowing the user to get creative. Create macros to simplify your
  configuration.
