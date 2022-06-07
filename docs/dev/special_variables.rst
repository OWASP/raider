Special variables
=================


.. _var_users:

_users
------

Setting this variable *is required* for **Raider** to run.

It should contain a list of dictionaries with the user credentials. For
now only usernames and passwords are evaluated, but in future it will be
used for other arbitrary user related information. This data gets
converted into a :class:`UserStore <raider.user.UserStore>` object which
provides a dictionary-like structure with :class:`User
<raider.user.User>` objects inside.

Example:

.. code-block:: hylang
		
    (setv _users
       [{:username "user1"
  	 :password "s3cr3tP4ssWrd1"}
        {:username "user2"
         :password "s3cr3tP4ssWrd2"}])   


.. _var_base_url:

_base_url
---------

This variable *is optional*.

Setting ``base_url`` will enable a shortcut for writing new
:class:`Request <raider.request.Request>` objects. When enabled, the
Requests can be created using ``:path`` instead of ``:url``


