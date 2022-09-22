.. _beginner-tutorial:

Beginner Tutorial
========

This beginner tutorial will guide you through how to use Raider and
highlight why Raider is different than other web penetration tools 
available to the open source community.

Prerequisites
-------------

Raider assumes you are comfortable with the following:

   1. Basic scripting in Python
   2. Operating on the command line

Though the project itself is written in a combination of Python and
Lisp, all you need to begin using Raider to automate your web pentesting
is entry-level knowledge of Python and familiarity working on the
command line.

If you haven't already, install Raider following the instructions in
:ref:`Installing Raider <./install.html>`

Running Raider
-------------

Once you have confirmed that Raider is installed and operational by
running the `raider --help` command and seeing the expected output, you
are ready to run your first Raider project.

First run `raider ls` to see your configured projects. If this is your
first time running Raider, it should be empty. 

.. code-block:: bash
   
   $ raider ls
   Raider command line running.
   Here's a hint in cli.py! args: Namespace(command='ls', proxy=None, user=None, verbose=False)
   Configured projects
   $

.. note:: "Configured Projects" in Raider are folders containing short
          scripts referred to as config files which are evaluated by
          Raider.

Configured projects are stored by default in your `~/.config/raider/projects/` 
directory. Create a folder there now and name it `firstraid`. Create a
file in `firstraid` named `main.hy`. This file will contain your first
set of commands for Raider to execute. Open `main.hy` in your preferred
text editor and prepare to write your first Raider config file.











