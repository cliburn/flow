"""Factory module. 

Allows flexible instantiation of arbitrary objects from strings."""

def forname(modname, attname):
    """Create objects from strings."""
    return getattr(__import__(modname), attname)

def factory(modname, attname, *args, **kwargs):
    """Factory for arbitrary classes. Can also be used to return evaluated functions."""
    return forname(modname, attname)(*args, **kwargs)
