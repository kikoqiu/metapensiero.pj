# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- function transformations
# :Created:  mer 09 nov 2016 12:59:00 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
from functools import reduce
from metapensiero.pj.js_ast.expressions import JSSubscript
from metapensiero.pj.js_ast.literals import JSList

from metapensiero.pj.js_ast.statements import JSLetStatement


from ..js_ast import (
    JSAttribute,
    JSArrowFunction,
    JSAssignmentExpression,
    JSAsyncFunction,
    JSAsyncMethod,
    JSCall,
    JSClassConstructor,
    JSDict,
    JSExpressionStatement,
    JSFunction,
    JSGenFunction,
    JSGenMethod,
    JSGetter,
    JSMethod,
    JSName,
    JSRest,
    JSSetter,
    JSStatements,
    JSThis,
    JSVarStatement,
    JSKeySubscript,
)
from ..processor.util import body_local_names, walk_under_code_boundary

from . import _normalize_name


def _isyield(el):
    return isinstance(el, (ast.Yield, ast.YieldFrom))


def FunctionDef(t, x, fwrapper=None, mwrapper=None):

    is_method = isinstance(t.parent_of(x), ast.ClassDef)
    is_in_method = not x.name.startswith('fn_') and \
                   all(lambda p: isinstance(p, (ast.FunctionDef,
                                                ast.AsyncFunctionDef,
                                                ast.ClassDef)) \
                       for p in t.parents(x, stop_at=ast.ClassDef)) and \
                           isinstance(tuple(t.parents(x, stop_at=ast.ClassDef))[-1],
                                      ast.ClassDef) # Make sure a class is there

    is_generator = reduce(lambda prev, cur: _isyield(cur) or prev,
                          walk_under_code_boundary(x.body), False)

    #t.unsupported(x, not is_method and x.decorator_list, "Function decorators are"
    #              " unsupported yet")
    if not is_method and x.decorator_list:
        t.warn(x,  "Function decorators are"
                  " unsupported yet")

    t.unsupported(x, len(x.decorator_list) > 1, "No more than one decorator"
                  " is supported")

    if x.args.vararg or x.args.kwonlyargs or x.args.defaults or \
       x.args.kw_defaults or x.args.kwarg:
        t.es6_guard(x, "Arguments definitions other than plain params require "
                    "ES6 to be enabled")

    #t.unsupported(x, x.args.kwarg and x.args.kwonlyargs,
    #              "Keyword arguments together with keyword args accumulator"
    #              " are unsupported")

    #t.unsupported(x, x.args.vararg and (x.args.kwonlyargs or x.args.kwarg),
    #              "Having both param accumulator and keyword args is "
    #              "unsupported")

    is_classmethod=False
    is_staticmethod=False
    is_getter=False
    is_setter=False
    if is_method:
        if x.decorator_list:
            # decorator should be "property" or "<name>.setter" or "classmethod" or "staticmethod"
            fdeco = x.decorator_list[0]
            if isinstance(fdeco, ast.Name) and fdeco.id == 'property':
                is_getter=True
            elif (isinstance(fdeco, ast.Attribute) and  fdeco.attr == 'setter'
                  and isinstance(fdeco.value, ast.Name)):
                is_setter=True
            elif isinstance(fdeco, ast.Name) and (fdeco.id == 'classmethod'  ):
                is_classmethod=True
            elif isinstance(fdeco, ast.Name) and (fdeco.id == 'staticmethod' ):
                is_staticmethod=True
            else:
                t.unsupported(x, True, "Unsupported method decorator")
                

    name = _normalize_name(x.name)
    body = x.body
    # get positional arg names and trim self if present
    arg_names = [arg.arg for arg in x.args.args]
    arg_names_ext=[]
    
    initparamstatement=[]
    if is_method:
        if len(arg_names) > 0:
            if not (arg_names[0] == 'self' or (is_classmethod and arg_names[0] == 'cls')):
               initparamstatement.append(JSLetStatement((arg_names[0],),(JSThis(),)))
            arg_names = arg_names[1:]

    acc = JSRest(x.args.vararg.arg) if x.args.vararg else None
    if x.args.vararg:
        arg_names_ext.append(x.args.vararg.arg)
    defaults = x.args.defaults
    kw = x.args.kwonlyargs
    kwdefs = x.args.kw_defaults    
    kw_names = [k.arg for k in kw]
    if kw:
        kwargs = []
        for k, v in zip(kw, kwdefs):
            if v is None:
                kwargs.append(k.arg)
            else:
                kwargs.append(JSAssignmentExpression(k.arg, v))
    else:
        kwargs = None

    # be sure that the defaults equal in length the args list
    if isinstance(defaults, (list, tuple)) and len(defaults) < len(arg_names):
        defaults = ([None] * (len(arg_names) - len(defaults))) + list(defaults)
    elif defaults is None:
        defaults = [None] * len(arg_names)

    if x.args.kwarg:
        if kwargs is None:
            kwargs=[]
        kwargs.append(JSRest(x.args.kwarg.arg))


    # render defaults of positional arguments and keywords accumulator
    args = []
    for k, v in zip(arg_names, defaults):
        if v is None:
            args.append(k)
        else:
            args.append(JSAssignmentExpression(k, v))

    # local function vars
    if 'vars' in t.ctx:
        upper_vars = t.ctx['vars']
    else:
        upper_vars = set()
    local_vars = list((set(body_local_names(body)) - set(arg_names)) -
                      set(kw_names) -set(arg_names_ext) - upper_vars)
    t.ctx['vars'] = upper_vars | set(local_vars)
    if len(local_vars) > 0:
        local_vars.sort()
        initparamstatement.append(JSVarStatement(local_vars, [None] * len(local_vars)))
        
    if initparamstatement:
        body = JSStatements(
            *initparamstatement,
            *body
        )

    if is_generator:
        fwrapper = JSGenFunction
        mwrapper = JSGenMethod

    # If x is a method
    if is_method:
        cls_member_opts = {}
        if x.decorator_list:
            # decorator should be "property" or "<name>.setter" or "classmethod"
            fdeco = x.decorator_list[0]
            if isinstance(fdeco, ast.Name) and fdeco.id == 'property':
                deco = JSGetter
            elif (isinstance(fdeco, ast.Attribute) and  fdeco.attr == 'setter'
                  and isinstance(fdeco.value, ast.Name)):
                deco = JSSetter
            elif isinstance(fdeco, ast.Name) and (fdeco.id == 'classmethod' or fdeco.id == 'staticmethod' ):
                deco = None
                cls_member_opts['static'] = True
            else:
                t.unsupported(x, True, "Unsupported method decorator")
        else:
            deco = None

        if name == '__init__':
            result = JSClassConstructor(
                args, body, acc, kwargs
            )
        else:
            mwrapper = mwrapper or deco or JSMethod
            if mwrapper is JSGetter:
                result = mwrapper(
                    name, body,
                    **cls_member_opts
                )
            elif mwrapper is JSSetter:
                t.unsupported(x, len(args) == 0, "Missing argument in setter")
                result = mwrapper(
                    name, args[0], body,
                    **cls_member_opts
                )
            elif mwrapper is JSMethod:
                if name == '__len__':
                    result = JSGetter(
                        'length',
                        body,
                        **cls_member_opts
                    )
                elif name == '__str__':
                    result = JSMethod(
                        'toString',
                        [], body,
                        **cls_member_opts
                    )
                elif name == '__get__':
                    result = JSMethod(
                        'get',
                        [], body,
                        **cls_member_opts
                    )
                elif name == '__set__':
                    result = JSMethod(
                        'set',
                        [], body,
                        **cls_member_opts
                    )
                elif name == '__instancecheck__':
                    cls_member_opts['static'] = True
                    result = JSMethod(
                        '[Symbol.hasInstance]',
                        args, body,
                        **cls_member_opts
                    )
                else:
                    result = mwrapper(
                        name, args, body,
                        acc, kwargs,
                        **cls_member_opts
                    )
            else:
                result = mwrapper(
                    name, args, body,
                    acc, kwargs,
                    **cls_member_opts
                )
    # x is a function
    else:
        if is_in_method and fwrapper is None:
            # set the incoming py_node for the sourcemap
            fdef = JSArrowFunction(
                name, args, body, acc, kwargs
            )
            fdef.py_node = x
            result = JSStatements(
                JSVarStatement([str(name)], [None]),
                fdef
            )
        elif is_in_method and fwrapper in [JSGenFunction, JSAsyncFunction]:
            # set the incoming py_node for the sourcemap
            fdef = fwrapper(
                name, args, body, acc, kwargs
            )
            fdef.py_node = x
            # arrow functions cannot be generators, render them as normal
            # function and add a bind(self)
            result = JSStatements(
                fdef,
                JSExpressionStatement(
                    JSAssignmentExpression(
                        JSName(name),
                        JSCall(
                            JSAttribute(name, 'bind'),
                            [JSThis()]
                        )
                    )
                )
            )
        else:
            fwrapper = fwrapper or JSFunction
            result = fwrapper(
                name, args, body,
                acc, kwargs
            )
    return result


def AsyncFunctionDef(t, x):
    t.stage3_guard(x, "Async stuff requires 'stage3' to be enabled")
    return FunctionDef(t, x, JSAsyncFunction, JSAsyncMethod)
