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
Installing Raider.

Running Raider on the Command Line
----------------------------------

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
set of commands for Raider to execute. Create and open `main.hy` in your 
preferred text editor and prepare to write your first Raider config file.

Understanding the Syntax of Config Files
----------------------------------------

Config files in Raider are written in Hylang,
but the relevant syntax is simple enough that it is easily readable with
an entry-level understanding of Python.

To begin, add the following line to your `main.hy` file.

.. code-block:: hylang

   (print "Wow, my first Raider project!")

Now run `raider authenticate firstraid` on the command line. You should
see `\"Wow, my first Raider project!\"` followed by an error. Don't
worry about the error for now.

.. code-block:: bash
  
   $ raider authenticate firstraid
   Raider command line running.
   Here's a hint in cli.py! args: Namespace(command='authenticate', project='firstraid', proxy=None, user=None, verbose=False)
   cli.py:: Here's the args.project variable: firstraid
   Here's a hint in ~/raider.py! project: firstraid
   hello
   Traceback (most recent call last):
   # ignore the details of the error for now.

Congrats, you have written your first line of Hylang! The important
thing to notice here is that Hylang commands are encapsulated by 
parenthesis. Don't worry too much about the rest of the syntax. 
Intuition will start to kick in as you continue through this tutorial.

Next we'll write a full config file that automatically logs you into a
website.

Writing An Authentication Config File
-------------------------------------

Raider has three main modes: `shell`, `authenticate`, and `run`. In this
tutorial we will focus on the simplest of the three, `authenticate`.

An authentication config file requires at least one defined username and
password pair stored in a User type object and at least one defined
AuthFlow type object.

A User object, referred to in Raider as a User Plugin,  contains 
username and password pairs which can be accessed by other objects in 
Raider. Every configuration file must have a User Plugin defined even if
not directly used in the configuration or Raider will throw an error.

Let's add one to our main.hy file now.

.. code-block:: hylang
  
   (print "Wow, my first Raider project!")

   (setv users 
         (Users
           [{"defaultuser" "defaultpass"}]))

The `setv` in Hylang is similar to `var` in Python. It creates a
variable `users` which is set to a User object containing one username
password pair in the next two lines.

Moving onto the AuthFlow object...

An AuthFlow dictates the steps necessary for changing the authentication
state of an html request. Here is an example added to our main.hy file.

.. code-block:: hylang
   
   (print "Wow, my first Raider project!")

   (setv users 
         (Users                                      
           [{"defaultuser" "defaultpass"}]))         
   
   (setv complex_form_auth
         (AuthFlow
           :request (Request
             :url "https://authenticationtest.com/HTTPAuth/"
             :method "GET"
             :headers [(Header.basicauth "user" "pass")])
           :operations [(Print.headers["Location"])]))

Once again we use `setv` to create a variable, in this case `complex_form_auth`
and set it to an AuthFlow object. The request parameters are set in
`:request (Request $parameters$)`. Here we set the target url to a site
created by Robert Lerner for the purposes of testing authentication
methods. The method is set to GET. The headers are set with another
Raider plugin type, Header. You can read
the docs for more information the Header plugin. For now it's enough to
know that the Header.basicauth method accepts the parameters `\"user\"` 
and `\"pass\"` and uses them to craft a basic authentication header
which is added to the HTML request.

Finally, `:operations` defines what this configuration file does once it
has carried out the authentication, sent a request and received a
response. Here we set it using the Print Operation to print the response 
URL, identified in the Print.headers method as `\"Location\"`. 

Logging into AuthenticationTest.com with Raider
----------------------------------------------

You've written your first config file and you're now
ready to run your `firstraid` project! You can run it from the command
line with the line `raider authenticate firstraid` to see the following
output:

.. codeblock:: bash
   $ raider authenticate firstraid
   Raider command line running.
   Here's a hint in cli.py! args: Namespace(command='authenticate', project='firstraid', proxy=None, user=None, verbose=False)
   cli.py:: Here's the args.project variable: firstraid
   Here's a hint in ~/raider.py! project: firstraid
   Wow, my first Raider project!
   Hooray! The config file finished loading.
   HTTP response headers:
   Location: https://authenticationtest.com/loginSuccess/

Congratulations! You've successfully automated the process of logging
into a website with Raider. Next you'll want to look at the other flows
and plugins described in the Raider documentation. Happy pentesting!



