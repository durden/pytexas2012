# Talk of Lighting talks

1. Ways to call out
2. Weakref module
    - Object keeps reference to another object (ref counting)
    - weak reference - doesn't keep object alive accidentally
    - weakref.ref() allows for setting a callback to be called when an object
      is about to die
    - Good solution for caching
3. Emacs, Org-Babel and Python
4. Zope.schema
5. Intercepting method calls
    - tracecalls class decorator
    - decorates a class and prints every time an attribute is accessed
6. Creating an immutable type
    - Subclass an existing immutable type (tuple, string, etc.)
    - Must override __new__ because __init__ happens after the creation of the
      object and setting stuff there would violate the immutable idea!
7. Context Managers
    - Good for timers, transactions
