Frequently asked questions
==========================


What's this and why should I care?
----------------------------------

OWASP Raider was developed with the goal to improve web
:term:`authentication` testing. By now it has evolved and can be used
for all kinds of stateful HTTP processes. Raider allows
you to simulate complex systems while allowing you to control each
piece of data you get in and out of the system.

How does it work?
-----------------

It abstracts the client-server information exchange as a :term:`finite
state machine`. Each step comprises one request with inputs, one
response with outputs, arbitrary actions to do on the response, and
conditional links to other stages. Thus, a graph-like structure is
created.

Each Raider project is a directory containing a set of :term:`hyfiles
<hyfile>`. Raider evaluates them, and gives you back Python objects to
interact with the application.  Raider's configuration is inspired by
Emacs. hylang is used, which is LISP on top of Python. LISP is used
because of its "Code is Data, Data is Code" property. With the magic
of LISP macros generating configuration automatically becomes
easy. Flexibility is in its DNA, meaning it can be infinitely extended
with actual code.


What can I use Raider for?
--------------------------

You can use it for example to create, store, reproduce, and share
proof-of-concepts easily for HTTP attacks. With Raider you can also
search through your Projects, filter by hyfile, Flows, FlowGraphs,
etc... Then you run either just one step, or a chain of steps, so you
can automate and run tests on any HTTP process.

Even though it was designed with penetration testing in mind, it could
still be useful for other purposes, like testing APIs or automating
stuff. Due to its flexibility and modular architecture it's easy for
users to extend it as they want.


.. _faq_eval:

You're telling me it'll evaluate all user input? Isn't that unsafe?
-------------------------------------------------------------------

Yes, by making the decision to run real code inside configuration
files we made it possible to run malicious code. Which is why you
should **always write your own configuration**, and not copy it from
untrusted sources. Raider assumes you are acting like a responsible
adult if you're using this project. If the user wants to write an
Operation that will ``rm -rf`` something on their machine when a HTTP
response is received, who are we to judge? With that said, we don't
take any responsibility if using Raider makes your computer catch
fire, your company bankrupt, starts the third world war, leads to AI
taking over humanity, or anything else in between.


How do I run this?
------------------

Previously Raider didn't have a CLI interface, and could only be run
by writing scripts. Now, you have to create the hyfiles in your
favourite text editor, and run raider :ref:`from the terminal <cli>`.


Do I need to know Python and hylang in order to use Raider?
---------------------------------------------------------------

Depends on what you're trying to achieve. Raider has become much
easier to use since its inception. You still need to write
configuration in hylang, but it's pretty straightforward if you know
the HTTP protocol.

Once you need some extra features not already included with Raider,
you will have to :ref:`write your own plugins <custom_plugins>` and
:ref:`operations <custom_operations>` which means you'll have to get
your hands dirty with hylang.

Check the :ref:`prerequisites` page to learn more.


Why LISP?
---------

Because in LISP, code is data, and data is code. First iterations
through planning this project were done with a static configuration
file, experimenting with different formats. However, it turns out all
of those static formats had problems. They can't easily execute code,
they can't hold data structures, etc... Changing this to a Lisp file,
all those problems vanished away, and it gives the user the power to
add features easily without messing with the main code.

Check the :ref:`Why LISP/hylang` for more information.



Why is Raider using hylang?
---------------------------

Because the main code is written in Python. After deciding to choose
LISP for the new configuration format, I obviously googled "python
LISP", and found this project. Looking through the documentation
I realized it turns out to be the perfect fit for my needs.


Does it work on Windows?
------------------------

Probably not. I don't have enough time to test it on other platforms.


What about macOS? BSD? etc?
---------------------------

I didn't test it, but should probably work as long as it's unix-like.


How can I contribute?
---------------------

If you're interested in contributing, you can do so. After you managed
to set up your first application, figure out what could have been made
easier or better.

Then start writing new Plugins and Operations and share them either on
`Github`_.

Once you're familiar with the structure of the project, you can start
by fixing bugs and writing new features.

.. _privately with me: raider@raiderauth.com
.. _Github: https://github.com/OWASP/raider
