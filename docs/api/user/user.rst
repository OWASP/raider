.. _users:
.. module:: raider.user

Users
-----

Use the :class:`Users` class when setting up your users in :term:`hyfiles`
like this:

.. code-block:: hylang
   
    (setv users
          (Users
            [{"admin"             ;; username
              "password"          ;; password
              :nickname "admin"}  ;; extra optional data
             {"user1" "password1"
	     :attribute "blah"
	     :nickname "mynickname"
	     :email "admin@example.com"}]))

Create the Users object by giving it a `list
<https://docs.hylang.org/en/stable/syntax.html#hy.models.List>`_ where
each list item is a `dictionary
<https://docs.hylang.org/en/stable/syntax.html#dictionary-literals>`_
with user data. Each user entry is required to have at least on
``key:value`` pair which is assumed to be ``username:password`` and
can therefore be accessed by the :class:`Variable
<raider.plugins.basic.Variable>` :class:`Plugin
<raider.plugins.common.Plugin>` as ``(Variable "username")`` and
``(Variable "password")`` respectively.

To use the optional user data, do the same but replace
username/password with the symbol name you specified earlier, for
example ``(Variable "nickname")`` will return ``admin`` if the first
user is active and ``mynickname`` if the second one is.
	     

.. autoclass:: Users
   :members:

The :class:`Users` class inherits from :class:`DataStore
<raider.structures.DataStore>` where each element is a :class:`User`
class containing data about a single user:

.. autoclass:: User
   :members:
      
