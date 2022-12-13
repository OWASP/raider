.. _custom_operations:

Writing Custom Operations
=========================

.. module:: raider.operations

.. _operations_api:

In case the existing operations are not enough, the user can write
their own to add the new functionality. Those new operations should be
written in the project's configuration directory in a ".hy" file. To
do this, a new class has to be defined, which will inherit from
*Raider*'s Operation class:

.. autoclass:: Operation
   :members:

		
