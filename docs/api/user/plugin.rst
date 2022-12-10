.. _plugins:
.. module:: raider.plugins.common

Plugins
-------

:term:`Plugins <Plugin>` in **Raider** are pieces of code that are
used to get inputs from, and put them in the HTTP :term:`Request`,
and/or to extract some ``value`` from the :term:`Response`. This is
used to :ref:`facilitate the information exchange <architecture>`
between :ref:`Flows <flows>`. :term:`Plugins <Plugin>` act as inputs
when used inside the :ref:`Flow's <flows>` ``request`` attribute, and
as outputs when used in the ``outputs`` attribute.

Below there's a list of predefined :term:`Plugins <Plugin>`. The users
are also encouraged to :ref:`write their own plugins <plugin_api>`.


Common
++++++

Users most often won't need to use those unless they're writing their
own :term:`Plugins <Plugin>`. Common :term:`Plugins <Plugin>` are
mostly used as parent classes for other :term:`Plugins <Plugin>`.

Plugin
******

Use this class only when creating new :term:`Plugins <Plugin>`. Either
when :ref:`writing custom plugins <plugin_api>` in `hylang
<https://docs.hylang.org/en/master/>`_ or when adding new plugins to
the Raider main code. `Check the repository
<https://github.com/OWASP/raider/tree/main/raider/plugins>`_ for
inspiration.

:class:`Plugin` objects can be used **BOTH** as inputs in HTTP
:term:`Requests <Request>` and outputs from HTTP :term:`Responses
<Response>`.

:term:`Plugin's <Plugin>` behaviour can be controlled with following
flags:

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
   [...]

.. autoclass:: Plugin
   :members:

Parser
******

The :class:`Parser` :class:`Plugin` takes other :class:`Plugins
<Plugin>` as input, parses it, and extracts the piece of information
for further use. :class:`Parser` :class:`Plugins <Plugin>` can
**ONLY** be used as inputs.

.. autoclass:: Parser
   :members:

Processor
*********

The :class:`Processor` :class:`Plugin` encodes, decodes and otherwise
processes other :class:`Plugins <Plugin>`. :class:`Processor`
:class:`Plugins <Plugin>` can **ONLY** be used as inputs.

.. autoclass:: Processor
   :members:

Empty
*****

The :class:`Empty` :class:`Plugin` is unique in that it contains no
function or ``value``. Its only use is when fuzzing but no previous
``value`` is needed. :class:`Empty` :class:`Plugin` can **ONLY** be
used as inputs.

.. autoclass:: Empty
   :members:

Example:

.. code-block:: hylang

   (setv placeholder (Empty "placeholder"))

   (setv attack
     (Flow
       (Request.post
	 "https://example.com/"
	 :data
	 {"item" "123"
	  "filename" placeholder     ;; Sends empty filename by default.
	                             ;; When fuzzing use the payload string instead.
	 }
       

.. module:: raider.plugins.basic

Basic
+++++

Basic :class:`Plugins <Plugin>` are the most commonly used ones, that
don't depend on other plugins to get its ``value``. Basic
:class:`Plugins <Plugin>` can be used **BOTH** as inputs and outputs.


Variable
********

The :class:`Variable` :class:`Plugin <raider.plugins.common.Plugin>`
extracts the ``value`` defined in the :class:`User <raider.user.User>`
object. Use it to get the username/password or other extra information
about the :class:`User <raider.user.User>`. :class:`Variable`
:class:`Plugins <raider.plugins.common.Plugin>` can **ONLY** be used
as inputs.


.. autoclass:: Variable
   :members:	       

Example:

.. code-block:: hylang

   (setv users
         (Users
           [{"admin"                     ;; username
             "password"                  ;; password
             :nickname "admin"           ;; extra optional data
	     :email "admin@example.com"}
            {"user1" "password1"
            :attribute "blah"
            :nickname "mynickname"
            :email "abc@example.com"}]))
   
   (setv username (Variable "username"))
   (setv password (Variable "password"))
   (setv nickname (Variable "nickname"))


   (setv login
     (Flow
         (Request.post
	   "https://www.example.com/login"
	   :data
	   {"username" username          ;; Sends the active user's credentials
	    "password" password          ;; and the email in the respective fields.
	    "email" email}

.. _plugin_prompt:

Prompt
******

The prompt plugin accepts user input mid-flow. Use it when you don't
know in advance the data you will need to send, like in case of
:term:`multi-factor authentication (MFA)`. :class:`Prompt`
:class:`Plugins <raider.plugins.common.Plugin>` can **ONLY** be used
as inputs.

.. autoclass:: Prompt
   :members:

Example:

.. code-block:: hylang

   (setv username (Variable "username"))
   (setv password (Variable "password"))
   (setv mfa_code (Prompt "Input code here:"))      ;; Asks user for the MFA code.

   (setv multifactor
     (Flow
         (Request.post
	   "https://www.example.com/login"
           :data
	   {"username" username
	    "password" password
	    "otp" mfa_code}             ;; Sends the data from user's input in `otp`.

.. _plugin_cookie:      

Cookie
******

The :class:`Cookie` :class:`Plugin <raider.plugins.common.Plugin>`
extracts its ``value`` from the :term:`Response's <Response>`
:class:`Cookie` headers. :class:`Cookie` :class:`Plugins
<raider.plugins.common.Plugin>` can be used **BOTH** as inputs and
outputs.

.. autoclass:: Cookie
   :members:

Example:

.. code-block:: hylang

   (setv username (Variable "username"))
   (setv password (Variable "password"))
   (setv session_cookie (Cookie "PHPSESSID"))   ;; Defines `session_cookie` as a Cookie
                                                ;; object with the name `PHPSESSID`.


   (setv csrf_token                         ;; Extract CSRF token from cookies
     (Cookie.regex "([a-zA-Z0-9]{10})"))    ;; where its name is a 10 alphanumerical string.
						
   (setv access_token
     (Json                         ;; Uses the Json Plugin
       :name "access_token"        ;; To extract the access token
       :extract "token"))          ;; Stored in `token`.

   (setv initialization
     (Flow
         (Request.get
	   "https://www.example.com")
       :outputs [session_cookie                 ;; Extracts `PHPSESSID` from response.
                 csrf_token]                    ;; Extracts CSRF token using `Cookie.regex`.
       :operations [(Next "login")]))

   (setv login
     (Flow
         (Request.post
	   "https://www.example.com/login"
           :cookies [session_cookie             ;; Uses the `PHPSESSID` extracted above.

	             (Cookie "admin" "true")    ;; Sends a custom cookie named `admin`
		                                ;; and the value `true`.

		     csrf_token]                ;; Sends the CSRF token as a cookie.
	   :data
	   {"username" username
	    "password" password})))

   (setv my_function
     (Flow
       (Request.get
       "https://www.example.com/my_function"

       ;; Sends the cookie `mycookie` with the value of
       ;; `access_token` extracted from JSON.
       :cookies [(Cookie.from_plugin access_token "mycookie" )])))




Header
******

The :class:`Header` :class:`Plugin <raider.plugins.common.Plugin>`
extracts and sets new headers.  :class:`Cookie` :class:`Plugins
<raider.plugins.common.Plugin>` can be used **BOTH** as inputs and
outputs.

.. autoclass:: Header
   :members:

Example:

.. code-block:: hylang

   (setv access_token
         (Regex
           :name "access_token"                     ;; Extracts `access_token` using
           :regex "\"accessToken\":\"([^\"]+)\""))  ;; regular expressions.
      
   (setv user_id
     (Json                         ;; Uses the Json Plugin
       :name "user_id"             ;; To extract `user_id`.
       :extract "user_id"))


   (setv authheader (Header.bearerauth access_token))   ;; Defines bearer authorization header.
   (setv useragent (Header "User-Agent" "Mozilla/5.0")) ;; Static user agent.

   (setv username (Variable "username"))
   (setv password (Variable "password"))

   (setv login
     (Flow
         (Request.post
	   "https://www.example.com/login"
	   :headers [useragent                    ;; Sets the user agent.

	             (Headers.from_plugin         ;; Creates new header from ``user_id``
		       user_id                    ;; Plugin and uses it in the value of
		       "X-identification")        ;; X-identification customer header.
	   :data
	   {"username" username
	    "password" password})
       :outputs [access_token]))                  ;; Extracts the `access_token`.

   (setv my_function
     (Flow
       (Request.get
       "https://www.example.com/my_function"
       :headers [authheader])))




File
****

The File plugin sets the plugin's ``value`` to the contents of a provided file
and allows string substitution within the content.

.. autoclass:: File
   :members:	       

.. _plugin_command:

Command
*******

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
*****

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
****

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
****

The Json plugin extracts fields from JSON tables.

.. autoclass:: Json
   :members:	       

.. module:: raider.plugins.modifiers


Modifiers
+++++++++

Alter
*****

The Alter plugin extracts and alters the ``value`` of other plugins.

.. autoclass:: Alter
   :members:	       

Combine
*******

The Combine plugin concatenates the ``value`` of other plugins.

.. autoclass:: Combine
   :members:	       


      
.. module:: raider.plugins.parsers

Parsers
+++++++

Urlparser
*********

The URLParser plugin parses URLs and extracts elements from it.

.. autoclass:: Urlparser
   :members:	       

.. module:: raider.plugins.processors

Processors
++++++++++

Urlencode
*********

The Urlencode plugin URL encodes a processor plugin.

.. autoclass:: Urlencode
   :members:

Urldecode
*********

The Urldecode plugin URL decodes a processor plugin.

.. autoclass:: Urldecode
   :members:

B64encode
*********

The B64encode plugin base64 encodes a processor plugin.

B64decode
*********

The B64decode plugin base64 decodes a processor plugin.

.. autoclass:: B64decode
   :members:

.. _plugin_api:

