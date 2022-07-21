.. _plugins:
.. module:: raider.plugins.common

Plugins
=======

:term:`Plugins <Plugin>` in **Raider** are pieces of code that are
used to get inputs from, and put them in the HTTP request, and/or to
extract some values from the response. This is used to facilitate the
information exchange between :ref:`Flows <flows>`. Below there's a
list of predefined :term:`Plugins <Plugin>`. The users are also
encouraged to :ref:`write their own plugins <plugin_api>`.


Common
------

Users most often won't need to use those unless they're writing their
own :term:`Plugins <Plugin>`. Common :term:`Plugins <Plugin>` are
mostly used as parent classes for other :term:`Plugins <Plugin>`.

Plugin
++++++

Use this class only when creating new plugins. Either when
:ref:`writing custom plugins <plugin_api>` in hylang or when adding
new plugins to the Raider main code. `Check the repository
<https://github.com/OWASP/raider/tree/main/raider/plugins>`_ for
inspiration.

Plugin's behaviour can be controlled with following flags:

+---------------------------+------+
| NEEDS_USERDATA            | 0x01 |
+---------------------------+------+
| NEEDS_RESPONSE            | 0x02 |
+---------------------------+------+
| DEPENDS_ON_OTHER_PLUGINS  | 0x04 |
+---------------------------+------+
| NAME_NOT_KNOWN_IN_ADVANCE | 0x08 |
+---------------------------+------+


Combine the flags with boolean OR if you want to set more flags, for
example:

.. code-block::

   class MyPlugin(Plugin):
   def __init__(self, name):
       super().__init__(
           name=name,
           function=self.extract_html_tag,
           flags=Plugin.NEEDS_USERDATA|Plugins.NEEDS_RESPONSE,
       )
   

.. autoclass:: Plugin
   :members:

Parser
++++++

The Parser plugin parses other plugins.

.. autoclass:: Parser
   :members:

Processor
+++++++++

The Processor plugin encodes, decodes and otherwise processes other
plugins.

.. autoclass:: Processor
   :members:

Empty
+++++

The Empty plugin is unique in that it contains no function or value.

.. autoclass:: Empty
   :members:


.. module:: raider.plugins.basic

Basic
-----

.. _plugin_variable:

Variable
++++++++

The Variable plugin extracts the values defined in the :class:`Users`
object.

.. autoclass:: Variable
   :members:	       

Example:

.. code-block:: hylang

   (setv username (Variable "username"))

.. _plugin_prompt:

Prompt
++++++

The prompt plugin accepts user input mid-flow.

.. autoclass:: Prompt
   :members:

Example:

.. code-block:: hylang

   (setv mfa_code (Prompt "Input code here:"))

.. _plugin_cookie:      

Cookie
++++++

The cookie plugin extracts and sets new cookies.

.. autoclass:: Cookie
   :members:

Example:

.. code-block:: hylang

   (setv session_cookie (Cookie "PHPSESSID"))


.. _plugin_header:      

Header
++++++

The Header plugin extracts and sets new headers.

.. autoclass:: Header
   :members:

Example:

.. code-block:: hylang

   (setv x-header (Header "x-header"))
   (setv y-header (Header "y-header" "y-value"))

   (setv z-header (Header.basicauth "username" "password"))


   (setv access_token
         (Regex
           :name "access_token"
           :regex "\"accessToken\":\"([^\"]+)\""))
      
   (setv z-header (Header.bearerauth access_token))


File
++++

The File plugin sets the plugin's value to the contents of a provided file
and allows string substitution within the content.

.. autoclass:: File
   :members:	       

.. _plugin_command:

Command
+++++++

The Command plugin runs shell commands and extracts their output. 

.. autoclass:: Command
   :members:

Example:

.. code-block:: hylang

   (setv mfa_code (Command
                   :name "otp"
		   :command "pass otp personal/app1"))


.. _plugin_regex:

Regex
+++++

The Regex plugin extracts a matched expression from the HTTP response.

.. autoclass:: Regex
   :members:

Example:

.. code-block:: hylang
		
   (setv access_token
         (Regex
           :name "access_token"
           :regex "\"accessToken\":\"([^\"]+)\""))


.. _plugin_html:      

Html
++++

The Html plugin extracts tags matching attributes specified by the user.

.. autoclass:: Html
   :members:

Example:

.. code-block:: hylang
		
    (setv csrf_token
          (Html
            :name "csrf_token"
            :tag "input"
            :attributes
            {:name "csrf_token"
             :value "^[0-9a-f]{40}$"
             :type "hidden"}
            :extract "value"))


.. _plugin_json:
      
Json
++++

The Json plugin extracts fields from JSON tables.

.. autoclass:: Json
   :members:	       

.. module:: raider.plugins.modifiers


Modifiers
---------

Alter
+++++

The Alter plugin extracts and alters the value of other plugins.

.. autoclass:: Alter
   :members:	       

Combine
+++++++

The Combine plugin concatenates the values of other plugins.

.. autoclass:: Combine
   :members:	       


      
.. module:: raider.plugins.parsers

Parsers
-------

UrlParser
+++++++++

The URLParser plugin parses URLs and extracts elements from it.

.. autoclass:: UrlParser
   :members:	       

.. module:: raider.plugins.processors

Processors
----------

Urlencode
+++++++++

The Urlencode plugin URL encodes a processor plugin.

.. autoclass:: Urlencode
   :members:

Urldecode
+++++++++

The Urldecode plugin URL decodes a processor plugin.

.. autoclass:: Urldecode
   :members:

B64encode
+++++++++

The B64encode plugin base64 encodes a processor plugin.

B64decode
+++++++++

The B64decode plugin base64 decodes a processor plugin.

.. autoclass:: B64decode
   :members:

.. _plugin_api:

Writing custom plugins
----------------------


In case the existing plugins are not enough, the user can write
their own to add the new functionality. Those new plugins should be
written in the project's configuration directory in a ".hy" file. To
do this, a new class has to be defined, which will inherit from
*Raider*'s Plugin class:


Let's assume we want a new plugin that will use `unix password store
<https://www.passwordstore.org/>`_ to extract the OTP from our website.


.. code-block:: hylang


    (defclass PasswordStore [Plugin]
    ;; Define class PasswordStore which inherits from Plugin

      (defn __init__ [self path]
      ;; Initiatialize the object given the path

        (.__init__ (super)
                   :name path
                   :function (. self run_command)))
      ;; Call the super() class, i.e. Plugin, and give it the
      ;; path as the name identifier, and the function
      ;; self.run_command() as a function to get the value.
      ;;
      ;; We don't need the response nor the user data to use
      ;; this plugin, so no flags will be set.
		   
      (defn run_command [self]
        (import os)
	;; We need os.popen() to run the command
	
        (setv self.value
              ((. ((. (os.popen
                        (+ "pass otp " self.path))
                      read))
                  strip)))
	;; set self.value to the output from "pass otp",
	;; with the newline stripped.
	
        (return self.value)))


And we can create a new variable that will use this class:

.. code-block:: hylang

    (setv mfa_code (PasswordStore "personal/reddit"))


Now whenever we use the ``mfa_code`` in our requests, its value will
be extracted from the password store.


      
