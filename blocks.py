#coding: utf8
import copy
from collections import OrderedDict


__all__ = ['Base', 'Comment', 'KeyOption', 'KeyValueOption', 'Block', 'EmptyBlock']


class Base(object):
    def get_indent(self, indent_level=0, indent_char=' ', indent=4, *args, **kwargs):
        return indent_char * indent * indent_level

    def render(self, name, *args, **kwargs):
        return '\n%(indent)s%(name)s' % {
            'name': name,
            'indent': self.get_indent(*args, **kwargs),
        }


class Comment(Base):
    _offset = ''
    _comment = ''

    def __init__(self, offset='', comment='', *args, **kwargs):
        self._offset = offset
        self._comment = comment
        super(Comment, self).__init__(*args, **kwargs)

    def render(self, name, *args, **kwargs):
        return '%(offset)s#%(comment)s' % {
            'offset': self._offset,
            'comment': self._comment,
        }


class KeyOption(Base):
    def render(self, name, *args, **kwargs):
        return '%s;' % super(KeyOption, self).render(name, *args, **kwargs)


class KeyValueOption(Base):
    def __str__(self):
        return str(self._value)

    def __init__(self, value='', *args, **kwargs):
        self._value = value
        super(KeyValueOption, self).__init__(*args, **kwargs)

    def val(self, val):
        self._value = val

    def render(self, name, *args, **kwargs):
        return super(KeyValueOption, self).render(
            '%(name)s %(value)s;' % {
                'name': name,
                'value': self._value
            }, *args, **kwargs)


class BlockMeta(type):
    def __new__(cls, name, bases, attrs):
        new_attrs = {'__options': {}}
        for attrname, attr in attrs.items():
            if issubclass(type(attr), Base):
                new_attrs['__options'].update({attrname: attr})
            else:
                new_attrs[attrname] = attr
        return super(BlockMeta, cls).__new__(cls, name, bases, new_attrs)


class Block(Base):
    __metaclass__ = BlockMeta

    def add_comment(self, comment):
        self._comments_count += 1
        name = 'comment{0}'.format(self._comments_count)
        setattr(self, name, comment)

    def __new__(cls):
        obj = super(Base, cls).__new__(cls)
        super(Block, obj).__setattr__('_options', [])
        super(Block, obj).__setattr__('_comments_count', 0)
        if hasattr(cls, '__options'):
            for attrname, attr in getattr(cls, '__options').items():
                setattr(obj, attrname, copy.deepcopy(attr))
        return obj

    def __setattr__(self, attr, value):
        if issubclass(type(value), Base):
            super(Block, self).__setattr__(attr, value)
            if not attr in self._options:
                self._options.append(attr)
        elif attr in self._options:
            getattr(self, attr).val(value)
        elif type(value) in [int, str]:
            super(Block, self).__setattr__(attr, value)

    def __setitem__(self, attr, value):
        return self.__setattr__(attr, value)

    def __getitem__(self, attr):
        return getattr(self, attr)

    def __delattr__(self, attr):
        del self._options[self._options.index(attr)]
        super(Block, self).__delattr__(attr)

    def render(self, name='', indent_level=0, indent=4, indent_char=' '):
        options = ''.join([
            getattr(self, key_name).render(key_name, indent_level + 1, indent_char, indent)
                for key_name in self._options])
        return '\n%(indent)s%(name)s{\n%(options)s\n%(indent)s}' % {
            'name': '%s ' % name if name else '',
            'options': options,
            'indent': self.get_indent(indent_level, indent_char, indent),
        }


class EmptyBlock(Block):
    def render(self, indent_level=0, indent=4, indent_char=' '):
        return ''.join([
            getattr(self, key_name).render(key_name, indent_level, indent_char, indent)
                for key_name in self._options])
