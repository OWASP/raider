Installing Raider
=================

The package is available in the `Python Package Index
<https://pypi.org/>`_, so to install the latest stable release of
*Raider* just use the command ``pip install raider``


If you want to build *Raider* from source, you can do so easily. You
will need to do that anyways if you want to contribute.

First start by clonning the repository with ``git clone
https://github.com/OWASP/raider``.

Using a python virtual environment is recommended to avoid weird
issues with python incompatibilities when working on the code. However
you can still use ``pip3 install .`` in the project's directory to
install the package locally.

Install the virtual environment, `install poetry
<https://python-poetry.org/docs/#installation>`_ and you can prepare
the virtual environment and switch to it to work with *Raider*:

.. code-block:: bash

   cd raider
   poetry install
   poetry shell


And now you're working inside the virtual environment, and *Raider*
should be available here.

Test it by running `raider --help` command:

.. code-block:: bash

   raider --help
   usage: raider [-h] [--proxy PROXY] [--verbose] [--user USER] {shell,authenticate,run,ls} ...
   
   positional arguments:
     {shell,authenticate,run,ls}
                           Command
       shell               Run commands in an interactive shell
       authenticate        Authenticate and exit
       run                 Authenticate, run function (or chain of functions) and exit
       ls                  List configured projects
   
   options:
     -h, --help            show this help message and exit
     --proxy PROXY         Send the request through the specified web proxy
     --verbose, -v         Verbose mode
     --user USER           Set up the active user
