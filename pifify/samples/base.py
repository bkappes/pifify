import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__) + \
                os.path.sep + os.path.pardir))
# this is specific the location of pypif, since I haven't
# installed pypif
sys.path.append('/Users/bkappes/src/citrine/pypif')
from pypif import pif


class SampleMeta(type):
    """
    Ensure a common interface for all sample classes, specifically,
    this ensures that all classes that use *SampleMeta* as a metaclass
    have a __getattr__ and a __setattr__ that automatically adds getter
    setter properties (practically -- this doesn't actually use the python
    property object).

    To use this metaclass, simply include:

        __metaclass__ = SampleMeta

    in any class that is to use this interface.
    """
    _prep = {}
    _props = {}

    def __new__(cls, name, parents, dct):
        dct['__getattr__'] = SampleMeta.getattr
        dct['__setattr__'] = SampleMeta.setattr
        dct['__contains__'] = SampleMeta.contains
        return super(SampleMeta, cls).__new__(cls, name, parents, dct)

    @staticmethod
    def attribute_generator(cls, name, rval):
        """Creates a new attribute for type CLS"""
        if not hasattr(cls, name):
            setattr(cls, name, lambda instance: rval)

    @staticmethod
    def contains(inst, key):
        cls = type(inst)
        return (key in cls._prep) or (key in cls._props)

    @staticmethod
    def getattr(inst, key):
        cls = type(inst)
        haskey = ((key in cls._prep) or \
                  (key in cls._props))
        if haskey and not hasattr(cls, key):
            return None
        return super(cls, inst).__getattr__(key)

    @staticmethod
    def setattr(inst, key, *args):
        cls = type(inst)
        # is the key in the preparation or properties dictionary?
        if key in cls._prep:
            dct = cls._prep
            if not isinstance(inst.printing.details, list):
                inst.printing.details = []
            dest = inst.printing.details
        elif key in cls._props:
            dct = cls._props
            if not isinstance(inst.properties, list):
                inst.properties = []
            dest = inst.properties
        else:
            dct = None
        if dct:
            # set the value
            value = dct[key](*args)
            # add the properties to the sample properties list
            dest.append(value)
            # store convenient access to this property
            # if more than one property is given the same name, then only
            # the most recent will retain programmatic access through the
            # attribute. However, both will be stored in the properties
            # field
            SampleMeta.attribute_generator(cls, key, value)
        else:
            attr = key
            value = args[0]
            super(cls, inst).__setattr__(attr, value)
#end 'class SampleMeta(type):'


def value_factory(name, **kwds):
    """
    Value factory

    Returns a function that accepts one or more scalar values and returns
    a named pif.Value object.

    Arguments
    ---------
    :name, str: Name of the value

    Keywords
    --------
    All keywords are passed into pif.Value.
    """
    kwds['name'] = name
    def func(x):
        kwds['scalars'] = x
        return pif.Value(**kwds)
    return func
# preparation_factory is nothing more than a value_factory whose return
# value is meant to be stored in a ProcessStep object
preparation_factory = value_factory


def property_factory(name, **kwds):
    """
    Property factory

    Returns a function that accepts one or more scalar values and returns
    a named pif.Property object.

    Arguments
    ---------
    :name, str: Name of the property

    Keywords
    --------
    All keywords are passed into pif.Property.
    """
    kwds['name'] = name
    def func(x):
        kwds['scalars'] = x
        return pif.Property(**kwds)
    return func
