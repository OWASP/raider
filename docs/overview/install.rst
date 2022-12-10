Installing Raider
=================

The package is available in the `Python Package Index
<https://pypi.org/>`_, so to install the latest stable release of
*Raider* just use the command ``pip install --upgrade raider``


If you want to build *Raider* from source, you can do so easily. You
will need to do that anyways if you want to contribute.

First start by clonning the repository with ``git clone
https://github.com/OWASP/raider``.

Using a python virtual environment is recommended to avoid weird
issues with python incompatibilities when working on the code. However
you can still use ``pip install .`` in the project's directory to
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

   usage: raider [-h] {show,config,new,delete,edit,inspect,run,shell} ...
   
   positional arguments:
     {show,config,new,delete,edit,inspect,run,shell}
                           Command
       show                Show projects/hyfiles/flows,etc...
       config              Configure raider
       new                 Create new projects and hyfiles
       delete              Delete projects and hyfiles
       edit                Edit projects and hyfiles
       inspect             Inspect Raider configuration
       run                 Run Flow or Flowgraph
       shell               Run commands in an interactive shell
   
   options:
     -h, --help            show this help message and exit
