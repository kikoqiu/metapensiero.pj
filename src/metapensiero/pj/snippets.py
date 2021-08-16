# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- code to aid transformation, it gets converted
# :Created:  mar 01 mar 2016 01:42:26 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#


def _in(left, right):
    from __globals__ import Array, typeof

    if isinstance(right, Array) or typeof(right) == 'string':
        return right.indexOf(left) > -1
    else:
        return left in right


def in_es6(left, right):
    from __globals__ import Array, typeof, Map, Set, WeakMap, WeakSet

    if isinstance(right, Array) or typeof(right) == 'string':
        return right.indexOf(left) > -1
    elif isinstance(right, (Map, Set, WeakMap, WeakSet)):
        return right.has(left)
    else:
        return left in right


def set_decorators(cls, props):
    from __globals__ import Function, Map, WeakMap, Object

    for p in dict(props):
        decos = props[p]
        def reducer(val, deco):
            return deco(val, cls, p)
        deco = decos.reduce(reducer, cls.prototype[p])
        if not isinstance(deco, (Function, Map, WeakMap)) and \
            isinstance(deco, Object) and (('value' in deco) or
                                          ('get' in deco)):
            del cls.prototype[p]
            Object.defineProperty(cls.prototype, p, deco)
        else:
            cls.prototype[p] = deco


def set_class_decorators(cls, decos):
    def reducer(val, deco):
        return deco(val, cls)
    return decos.reduce(reducer, cls)


def set_properties(cls, props):
    from __globals__ import Function, Map, WeakMap, Object

    for p in dict(props):
        value = props[p]
        if not isinstance(value, (Map, WeakMap)) and isinstance(value, Object) \
           and 'get' in value and isinstance(value.get, Function):
            # the following condition raises a TypeError in dukpy, why?
            # ('set' in value and isinstance(value.set, Function)):
            desc = value
        else:
            desc = {
                'value': value,
                'enumerable': False,
                'configurable': True,
                'writable': True
            }
        Object.defineProperty(cls.prototype, p, desc)


def _assert(comp, msg):
    from __globals__ import Error, Object, typeof

    def PJAssertionError(self, message):
        self.name = 'PJAssertionError'
        self.message = message or 'Custom error PJAssertionError'
        if typeof(Error.captureStackTrace) == 'function':
            Error.captureStackTrace(self, self.constructor)
        else:
            self.stack = Error(message).stack

    PJAssertionError.prototype = Object.create(Error.prototype)
    PJAssertionError.prototype.constructor = PJAssertionError

    msg = msg or 'Assertion failed.'
    if not comp:
        raise PJAssertionError(msg)



def mapl(arr, mapper, filter=None):
    return [*mapg(arr,mapper,filter)]
        

def mapg(arr, mapper, filter=None):
    if filter:
        for a in arr:
            if filter(a):
                yield mapper(a)
    else:
        for a in arr:
            yield mapper(a)

def ext_acc(*acc):
    last=acc[-1]
    kwargs=None
    if isinstance(last,_pj.kw):
        kwargs=last.values
        return acc[:-1],kwargs
    return acc,

class kw:
    def __init__(self, values):
        self.values = values
    def setdefault(self,key,val):
        if not key in self:
            self[key]=val


def pythonset():
    return JS('new Set()')

def subscript(arr,lower,upper,step):
    return JS('new subscript()')