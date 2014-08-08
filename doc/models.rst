
Filtration
==========

Class Attributes
----------------

The following class attributes are used:

verbose_name (from meta)

This is used to give the friendly name of the class in the filtration tree

top_level_filter (Class attribute)

If true, this class will appear in the top level of the filter tree, if false it will only appear through references

relation_to_attempts (Class attribute)

String used to determine how to filter attempts using this model, generally the name of the foreign key field

no_filter_fields (Class attribute)

Array of fields that should not be used to create filters.


Models
=======

.. automodule:: lavaFlow.models
    :members:
    :undoc-members:
    :private-members:
    :special-members:

