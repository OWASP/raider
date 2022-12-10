.. _flows:

Flows
-----

:term:`Flows <Flow>` are the main concept in **Raider**, used to
define the HTTP information exchange. Each :term:`request` you want to
send needs its own Flow object. Inside the ``request`` attribute of
the object, needs to be a :class:`Request <raider.request.Request>`
object containing the definition of the ``request``.

This definition can contain :class:`Plugins <raider.plugins.Plugin>`
whose value will be used when sending the HTTP :term:`Request`. In
this case, the :class:`Plugins <raider.plugins.Plugin>` will act as
inputs.

When using :class:`Plugins <raider.plugins.Plugin>` in the ``outputs``
attribute, they will act as outputs, and the ``value`` will be
extracted for later use.

.. automodule:: raider.flow
   :members:
   :undoc-members:


Examples
++++++++

Create the variable ``initialization`` with the Flow. It'll send a
GET request to ``https://example.com/admin/``. If the HTTP response
code is 200 go to next stage ``login``.

.. code-block:: hylang

    (setv initialization
          (Flow
            (Request.get
	      "https://example.com/admin/")
            :operations [(Http
                           :status 200
                           :action (Next "login"))]))
    

Define Flow ``login``. It will send a POST request to
``https://example.com/admin/login`` with the username and the password
in the body. Extract the cookie ``PHPSESSID`` and store it in the
``session_id`` plugin. If server responds with HTTP 200 OK, print
``login successfully``, otherwise quit with the error message ``login
error``.

.. code-block:: hylang

    (setv username (Variable "username"))
    (setv password (Variable "password"))
    (setv session_id (Cookie "PHPSESSID"))

    (setv login
          (Flow
            (Request.post
	       "https://www.example.com/admin/login"
               :data
               {"password" password
               "username" username})
            :outputs [session_id]
            :operations [(Http
                           :status 200
                           :action (Print "login successfully")
                           :otherwise (Error "login error"))]))
    		


Define another ``login`` Flow. Here what's different is the
``csrf_name`` and ``csrf_value`` plugins. In this application both the
name and the value of the token needs to be extracted, since they change
all the time. They were defined as :class:`Html <raider.plugins.Html>`
objects. Later they're being used in the body of the :class:`Request
<raider.request.Request>`.

If the HTTP response code is 200 means the :term:`MFA <Multi-factor
authentication (MFA)>` was enabled and the ``multi_factor`` stage
needs to run next. Otherwise, try to log in again. Here the password
is asked from the user by a :class:`Prompt <raider.plugins.Prompt>`.

.. code-block:: hylang

    ;; Gets `username` from active user's object defined in `users`.
    (setv username (Variable "username"))

    ;; Gets the password by manual input.
    (setv password (Prompt "password"))

    ;; Gets `PHPSESSID` from the cookie.
    (setv session_id (Cookie "PHPSESSID"))

    ;; Gets the OTP code by manual input.
    (setv mfa_code (Prompt "OTP code"))

    ;; Extract nickname from the HTML code. It looks for a tag like this:
    ;; <input id="nickname" value="admin">
    ;; and returns `admin`.
    (setv nickname
          (Html
            :name "nickname"
            :tag "input"
            :attributes
            {:id "nickname"}
            :extract "value"))

    ;; Extracts the name of the CSRF token from HTML code. It looks
    ;; for a tag similar to this:
    ;; <input name="0123456789" value="0123456789012345678901234567890123456789012345678901234567890123" type="hidden">
    ;; and returns 0123456789.
    (setv csrf_name
          (Html
            :name "csrf_name"
            :tag "input"
            :attributes
            {:name "^[0-9A-Fa-f]{10}$"
             :value "^[0-9A-Fa-f]{64}$"
             :type "hidden"}
            :extract "name"))

    ;; Extracts the value of the CSRF token from HTML code. It looks
    ;; for a tag similar to this:
    ;; <input name="0123456789" value="0123456789012345678901234567890123456789012345678901234567890123" type="hidden">
    ;; and returns 0123456789012345678901234567890123456789012345678901234567890123.    
    (setv csrf_value
          (Html
            :name "csrf_value"
            :tag "input"
            :attributes
            {:name "^[0-9A-Fa-f]{10}$"
             :value "^[0-9A-Fa-f]{64}$"
             :type "hidden"}
            :extract "value"))

    ;; Defines the `login` Flow. Sends a POST request to
    ;; https://example.com/login.php. Use the username, password
    ;; and both the CSRF name and values in the POST body.
    ;; Extract the new CSRF values, and moves to the next stage
    ;; if HTTP response is 200.
    (setv login
          (Flow
            (Request.post
               "https://example.com/login.php"
               :cookies [session_id]
               :data
               {"password" password
               "username" username
               csrf_name csrf_value})
            :outputs [csrf_name csrf_value]
            :operations [(Http
                           :status 200
                           :action (Next "multi_factor")
                           :otherwise (Next "login"))]))

    ;; Defines the `multi_factor` Flow. Sends a POST request to
    ;; https://example.com/login.php. Use the username, password,
    ;; CSRF values, and the MFA code in the POST body.
    (setv multi_factor
          (Flow
            (Request.post
	       "https://example.com/login.php"
               :cookies [session_id]
               :data
               {"password" password
                "username" username
	        "otp" mfa_code
                csrf_name csrf_value})
            :outputs [csrf_name csrf_value]))

    ;; Extracts the nickname and print it. Send a GET request to
    ;; https://example.com/settings.php and extract the nickname
    ;; from the HTML response.
    (setv get_nickname
          (Flow
            (Request.get
	      "https://example.com/settings.php"
              :cookies [session_id])
            :outputs [nickname]
	    :operations [(Print nickname)]))
		
