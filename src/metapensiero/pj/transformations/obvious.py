# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- simpler transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>,
#            Lele Gaifax <lele@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
from functools import reduce

from metapensiero.pj.js_ast.expressions import JSExpression, JSNewCall
from metapensiero.pj.js_ast.functions import JSFunction
from metapensiero.pj.js_ast.noops import JSCommentBlock
from metapensiero.pj.js_ast.statements import JSLetStatement, JSVarStatement

from ..compat import is_py39
from . import _normalize_name, _normalize_attribute_name,_normalize_dict_keys

from ..js_ast import (
    JSAssignmentExpression,
    JSArrowFunction,
    JSAttribute,
    JSAugAssignStatement,
    JSAwait,
    JSBinOp,
    JSBreakStatement,
    JSCall,
    JSContinueStatement,
    JSDeleteStatement,
    JSDict,
    JSExport,
    JSExpressionStatement,
    JSFalse,
    JSIfExp,
    JSIfStatement,
    JSList,
    JSName,
    JSNull,
    JSNum,
    JSOpAdd,
    JSOpAnd,
    JSOpBitAnd,
    JSOpBitOr,
    JSOpBitXor,
    JSOpDiv,
    JSOpGt,
    JSOpGtE,
    JSOpIn,
    JSOpInvert,
    JSOpLShift,
    JSOpLt,
    JSOpLtE,
    JSOpMod,
    JSOpMult,
    JSOpNot,
    JSOpOr,
    JSOpRShift,
    JSOpSub,
    JSOpUSub,
    JSOpUAdd,
    JSPass,
    JSRest,
    JSReturnStatement,
    JSStatements,
    JSStr,
    JSSubscript,
    JSTemplateLiteral,
    JSTrue,
    JSUnaryOp,
    JSWhileStatement,
    JSYield,
    JSYieldStar,
    JSOpPow,
)


#### Statements


def Assign_default(t, x):
    y = JSAssignmentExpression(x.targets[-1], x.value)
    for i in range(len(x.targets) - 1):
        y = JSAssignmentExpression(x.targets[-(2 + i)], y)
    return JSExpressionStatement(y)


# Python 3.6+ typehints are accepted and ignored
def AnnAssign(t, x):
    return JSExpressionStatement(JSAssignmentExpression(x.target, x.value))

def Assign_all(t, x):
    if len(x.targets) == 1 and isinstance(x.targets[0], ast.Name) and \
       x.targets[0].id == '__all__':
        t.es6_guard(x, "'__all__' assignment requires ES6")
        t.unsupported(x, not isinstance(x.value, (ast.Tuple, ast.List)),
                      "Please define a '__default__' member for default"
                      " export.")
        elements = x.value.elts
        return JSExport([el.s for el in elements
                         if not t.unsupported(el, not isinstance(el, ast.Str),
                         'Must be a string literal.')])


def Assign_setitem(t, x):
    if len(x.targets) == 1 and isinstance(x.targets[0], ast.Subscript) and isinstance(x.targets[0].slice, ast.ExtSlice):
        return JSCall(JSAttribute(JSName('_pj'), '__setitem__'), [x.targets[0].value, x.targets[0].slice, x.value])



def AugAssign(t, x):
    if isinstance(x.op, ast.FloorDiv):
        return JSAssignmentExpression(x.target, JSCall(
            JSAttribute(
                JSName('Math'),
                'floor'),
            [JSBinOp(x.target, JSOpDiv(), x.value)]) )
    return JSAugAssignStatement(x.target, x.op, x.value)


def If(t, x):
    return JSIfStatement(x.test, x.body, x.orelse)


def While(t, x):
    if not x.orelse:
        return JSWhileStatement(x.test, x.body)
    cond=JSName(t.new_name())
    return JSStatements(
        JSLetStatement((cond,),(None,)),
        JSWhileStatement(JSAssignmentExpression(cond, x.test), x.body),
        JSIfStatement(JSUnaryOp(JSOpNot(), cond),x.orelse,None)
    )


def Break(t, x):
    return JSBreakStatement()


def Continue(t, x):
    return JSContinueStatement()


def Pass(t, x):
    return JSPass()


def Return(t, x):
    # x.value is None for blank return statements
    return JSReturnStatement(x.value)


def Delete(t, x):
    js = []
    for t in x.targets:
        jd = JSDeleteStatement(t)
        if len(x.targets) == 1:
            jd.py_node = x
        else:
            jd.py_node = t
        js.append(jd)
    return JSStatements(*js)


def Await(t, x):
    t.stage3_guard(x, "Async stuff requires 'stage3' to be enabled")
    return JSAwait(x.value)


#### Expressions


def Expr_default(t, x):
    # See [pj.transformations.special](special.py) for special cases
    return JSExpressionStatement(x.value)


def List(t, x):
    return JSList(x.elts)


def Tuple(t, x):
    return JSList(x.elts)


def Dict(t, x):
    return JSDict(_normalize_dict_keys(t, x.keys), x.values)

def Set(t, x):
    ret=JSCall(
        JSAttribute(
            JSName('_pj'),
            'pythonset'),
        x.elts)
    return ret

def Lambda(t, x):
    assert not any(getattr(x.args, k) for k in [
            'vararg', 'kwonlyargs', 'kwarg', 'defaults', 'kw_defaults'])
    return JSArrowFunction(
                None,
                [arg.arg for arg in x.args.args],
                [JSReturnStatement(x.body)])


def IfExp(t, x):
    return JSIfExp(x.test, x.body, x.orelse)


def Call_default(t, x, operator=None,override_funcname=None):
    # See [pj.transformations.special](special.py) for special cases

    if x.keywords:
        # TODO: 
        # def test(a=1,b=1,c=1,*acc,**kwacc):
        #  pass
        # test(a=1)?
        kwkeys = []
        kwvalues = []
        for kw in x.keywords:
            #t.unsupported(x, kw.arg is None, "'**kwargs' syntax isn't "
            #              "supported")
            if kw.arg is None:
                print(kw.value)
                kwacc=kw.value
                #kwkeys.append(JSRest(JSName(kwacc)))
                kwkeys.append(JSRest(kwacc))
                kwvalues.append(None)                
            else:
                kwkeys.append(kw.arg)
                kwvalues.append(kw.value)

        kwargs = JSDict(_normalize_dict_keys(t, kwkeys), kwvalues)        
        kwargs=JSNewCall(
            JSAttribute(
                JSName('_pj'),
                'kw'),
            [kwargs])

    else:
        kwargs = None
    return JSCall(override_funcname or x.func, x.args, kwargs, operator)


def Attribute_default(t, x):
    return JSAttribute(x.value, _normalize_attribute_name(str(x.attr)))


def Subscript_default(t, x):
    v=None
    if is_py39 and isinstance(x.slice, (ast.Constant, ast.Name)):
        v = x.slice
    elif isinstance(x.slice, ast.Index):
        v = x.slice.value
    if v:
        if isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.USub):
            return JSSubscript(
                JSCall(JSAttribute(x.value, 'slice'), [v]),
                JSNum(0))
        return JSSubscript(x.value, v)
    return JSCall(JSAttribute(JSName('_pj'), '__getitem__'), [x.value,x.slice])
         
def ExtSlice(t,x):
    return JSList(x.dims)

def Slice(t,x):
    return JSNewCall(JSAttribute(JSName('_pj'), 'slice'), [
        JSNull() if x.lower is None else x.lower,
        JSNull() if x.step is None else x.step,
        JSNull() if x.upper is None else x.upper
        ])

def Index(t,x):
    return JSNum(x.value)

def UnaryOp(t, x):
    return JSUnaryOp(x.op, x.operand)


def BinOp_default(t, x):
    # See [pj.transformations.special](special.py) for special cases
    return JSBinOp(x.left, x.op, x.right)


def BoolOp(t, x):
    return reduce(
                lambda left, right: JSBinOp(left, x.op, right),
                x.values)


def Compare_default(t, x):
    """Compare is for those expressions like 'x in []' or 1 < x < 10. It's
    different from a binary operations because it can have multiple
    operators and more than two operands."""
    exps = [x.left] + x.comparators
    bools = []
    for i in range(len(x.ops)):
        bools.append(JSBinOp(exps[i], x.ops[i], exps[i + 1]))
    return reduce(lambda x, y: JSBinOp(x, JSOpAnd(), y), bools)


#### Atoms


def Num(t, x):
    if isinstance(x.n, (complex)):
        return JSNewCall(JSAttribute(JSName('_pj'),'complex'),[JSStr(str(x.n))])
    return JSNum(x.n)


def Str(t, x):
    return JSStr(x.s)


def JoinedStr(t, x):
    t.es6_guard(x, "f-strings require ES6")
    chunks = []
    for value in x.values:
        if isinstance(value, ast.Str):
            chunks.append(value.s)
        else:
            assert isinstance(value, ast.FormattedValue)
            t.unsupported(x, value.conversion != -1,
                          "f-string conversion spec isn't supported")
            t.unsupported(x, value.format_spec is not None,
                          "f-string format spec isn't supported")
            chunks.append('${%s}' % t._transform_node(value.value))
    return JSTemplateLiteral(''.join(chunks))


def Name_default(t, x):
    # {True,False,None} are Names
    cls = {
        'True': JSTrue,
        'False': JSFalse,
        'None': JSNull,
    }.get(x.id)
    if cls:
        return cls()
    else:
        n = x.id
        n = _normalize_name(n)
        return JSName(n)


def NameConstant(t, x):
    cls = {
        True: JSTrue,
        False: JSFalse,
        None: JSNull,
    }[x.value]
    return cls()


# Take care of Python 3.8's deprecations:
# https://docs.python.org/3/library/ast.html#node-classes
def Constant(t, x):
    if isinstance(x.value, bool) or x.value is None:
        return NameConstant(t, x)
    elif isinstance(x.value, (int, float, complex)):
        return Num(t, x)
    elif isinstance(x.value, str):
        return Str(t, x)
    else:
        # Should constant collections (tuple and frozensets
        # containing constant elements) be handled here as well?
        # See https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Constant
        raise ValueError('Unknown data type received.')


def Yield(t, x):
    return JSYield(x.value)


def YieldFrom(t, x):
    return JSYieldStar(x.value)


#### Ops


def In(t, x):
    return JSOpIn()


def Add(t, x):
    return JSOpAdd()


def Sub(t, x):
    return JSOpSub()


def USub(t, x):
    "Handles tokens like '-1'"
    return JSOpUSub()

def UAdd(t, x):
    "Handles tokens like '+(1)'"
    return JSOpUAdd()


def Mult(t, x):
    return JSOpMult()


def Div(t, x):
    return JSOpDiv()


def Pow(t, x):
    return JSOpPow()


def Mod(t, x):
    return JSOpMod()


def RShift(t, x):
    return JSOpRShift()


def LShift(t, x):
    return JSOpLShift()


def BitXor(t, x):
    return JSOpBitXor()


def BitAnd(t, x):
    return JSOpBitAnd()


def BitOr(t, x):
    return JSOpBitOr()


def Invert(t, x):
    return JSOpInvert()


def And(t, x):
    return JSOpAnd()


def Or(t, x):
    return JSOpOr()


def Not(t, x):
    return JSOpNot()


# == and != are in special.py
# because they transform to === and !==


def Lt(t, x):
    return JSOpLt()


def LtE(t, x):
    return JSOpLtE()


def Gt(t, x):
    return JSOpGt()


def GtE(t, x):
    return JSOpGtE()


def Starred(t, x):
    return JSRest(x.value)

def Global(t,x):#
    #see functions
    return JSCommentBlock('global '+','.join(x.names))