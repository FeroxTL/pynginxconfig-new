#coding: utf8
import copy
from collections import OrderedDict


class Base(object):
    def get_indent(self, indent_level=0, indent_char=' ', indent=4, *args, **kwargs):
        return indent_char * indent * indent_level

    def render(self, name, *args, **kwargs):
        return '\n%(indent)s%(name)s' % {
            'name': name,
            'indent': self.get_indent(*args, **kwargs),
        }


class KeyOption(Base):
    def render(self, name, *args, **kwargs):
        return '%s;' % super(KeyOption, self).render(name, *args, **kwargs)


class KeyValueOption(Base):
    def __str__(self):
        return str(self._value)

    #def __set__(self, obj, value):
    #    self._value = value
    #    super(KeyValueOption, self).__set__(obj, value)

    def __init__(self, value='', *args, **kwargs):
        self._value = value
        super(KeyValueOption, self).__init__(*args, **kwargs)

    def val(self, val):
        self._value = val

    def render(self, name, *args, **kwargs):
        return super(KeyValueOption, self).render(
            u'%(name)s = %(value)s;' % {
                'name': name,
                'value': self._value
            }, *args, **kwargs)


class BlockMeta(type):
    def __new__(cls, name, bases, attrs):
        new_attrs = {'__options': {}}
        for attrname, attr in attrs.iteritems():
            if issubclass(type(attr), Base):
                new_attrs['__options'].update({attrname: attr})
            else:
                new_attrs[attrname] = attr
        return super(BlockMeta, cls).__new__(cls, name, bases, new_attrs)


class Block(Base):
    _options = []
    __metaclass__ = BlockMeta

    def __new__(cls):
        obj = super(Base, cls).__new__(cls)
        if hasattr(cls, '__options'):
            for attrname, attr in getattr(cls, '__options').iteritems():
                setattr(obj, attrname, copy.deepcopy(attr))
        return obj

    def __setattr__(self, attr, value):
        if issubclass(type(value), Base):
            super(Block, self).__setattr__(attr, value)
            if not attr in self._options:
                self._options.append(attr)
        elif attr in self._options:
            getattr(self, attr).val(value)

    def __delattr__(self, attr):
        del self._options[self._options.index(attr)]
        super(Block, self).__delattr__(attr)

    def render(self, name='', indent_level=0, indent=4, indent_char=' '):
        options = u''.join([
            getattr(self, key_name).render(key_name, indent_level + 1, indent_char, indent)
                for key_name in self._options])
        return u'%(indent)s%(name)s{%(options)s\n%(indent)s}' % {
            'name': '%s ' % name if name else '',
            'options': options,
            'indent': self.get_indent(indent_level, indent_char, indent),
        }
