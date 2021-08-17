# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj -- comprehensions transformations
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
from metapensiero.pj.js_ast.functions import JSArrowFunction
from metapensiero.pj.js_ast.literals import JSNull
from metapensiero.pj.js_ast.operators import JSRest

from metapensiero.pj.js_ast.statements import JSYield

from ..js_ast import (
    JSAttribute,
    JSAugAssignStatement,
    JSBinOp,
    JSCall,
    JSExpressionStatement,
    JSForStatement,
    JSFunction,
    JSIfStatement,
    JSList,
    JSName,
    JSNum,
    JSOpAdd,
    JSOpLt,
    JSReturnStatement,
    JSSubscript,
    JSThis,
    JSVarStatement,
    JSForIterableStatement,
    JSGenFunction,
    JSKeySubscript,
    JSExpression,
)

#### ListComp
# Transform
# <pre>[EXPR for NAME in LIST]</pre>
# or
# <pre>[EXPR for NAME in LIST if CONDITION]</pre>
def ListComp_x(t, x):

    assert len(x.generators) == 1
    assert len(x.generators[0].ifs) <= 1
    assert isinstance(x.generators[0], ast.comprehension)
    assert isinstance(x.generators[0].target, ast.Name)

    EXPR = x.elt
    NAME = x.generators[0].target
    LIST = x.generators[0].iter
    if len(x.generators[0].ifs) == 1:
        CONDITION = x.generators[0].ifs[0]
    else:
        CONDITION = None

    __new = t.new_name()
    __old = t.new_name()
    __i = t.new_name()
    __bound = t.new_name()

    # Let's construct the result from the inside out:
    #<pre>__new.push(EXPR);</pre>
    push = JSExpressionStatement(
            JSCall(
                JSAttribute(
                    JSName(__new),
                    'push'),
                [EXPR]))

    # If needed, we'll wrap that with:
    #<pre>if (CONDITION) {
    #    <i>...push...</i>
    #}</pre>
    if CONDITION:
        pushIfNeeded = JSIfStatement(
                CONDITION,
                push,
                None)
    else:
        pushIfNeeded = push

    # Wrap with:
    #<pre>for(
    #        var __i = 0, __bound = __old.length;
    #        __i &lt; __bound;
    #        __i++) {
    #    var NAME = __old[__i];
    #    <i>...pushIfNeeded...</i>
    #}</pre>
    forloop = JSForStatement(
                    JSVarStatement(
                        [__i, __bound],
                        [0, JSAttribute(
                                JSName(__old),
                                'length')]),
                    JSBinOp(JSName(__i), JSOpLt(), JSName(__bound)),
                    JSAugAssignStatement(JSName(__i), JSOpAdd(), JSNum(1)),
                    [
                        JSVarStatement(
                            [NAME.id],
                            [JSSubscript(
                                JSName(__old),
                                JSName(__i))]),
                        pushIfNeeded])

    # Wrap with:
    #<pre>function() {
    #    var __new = [], __old = LIST;
    #    <i>...forloop...</i>
    #    return __new;
    #}
    func = JSFunction(
        None,
        [],
        [
            JSVarStatement(
                [__new, __old],
                [JSList([]), LIST]),
            forloop,
            JSReturnStatement(
                JSName(__new))])

    # And finally:
    #<pre>((<i>...func...</i>).call(this))</pre>
    invoked = JSCall(
            JSAttribute(
                func,
                'call'),
            [JSThis()])

    return invoked



#### ListComp
# Transform
# <pre>[EXPR for NAME in LIST]</pre>
# or
# <pre>[EXPR for NAME in LIST if CONDITION]</pre>
def ListComp(t, x):    
    comp = GeneratorExp(t,x,isListComp=True)
    return comp

def SetComp(t, x):    
    comp = GeneratorExp(t,x,isListComp=True)
    from ..snippets import pythonset
    t.add_snippet(pythonset)
    ret=JSCall(
        JSAttribute(
            JSName('_pj'),
            'pythonset'),
        [comp])
    return ret

#### GeneratorExp
# Transform
# <pre>EXPR for NAME in LIST</pre>
# or
# <pre>EXPR for NAME in LIST if CONDITION</pre>
def GeneratorExp(t, x, isListComp=False):
    if isListComp:
        helper_func=JSAttribute(JSName('_pj'), 'mapl')
    else:
        helper_func=JSAttribute(JSName('_pj'), 'mapl')
    
    #assert len(x.generators) == 1
    #t.unsupported(x,len(x.generators) > 1,'len(x.generators) > 1')
    assert len(x.generators[0].ifs) <= 1
    assert isinstance(x.generators[0], ast.comprehension)
    #assert isinstance(x.generators[0].target, ast.Name)
    t.unsupported(x,not isinstance(x.generators[0].target, ast.Name) and not isinstance(x.generators[0].target, ast.Tuple),'not isinstance(x.generators[0].target, ast.Name) and not isinstance(x.generators[0].target, ast.Tuple)')
    names=[]
    mappers=[]
    filters=[]
    for i, g in enumerate(x.generators):
        if i==len(x.generators)-1:
            EXPR = x.elt
        else:
            EXPR = x.generators[i+1].iter

        NAME = g.target
        LIST = g.iter
        if len(g.ifs) == 1:
            CONDITION = g.ifs[0]
        else:
            CONDITION = None

        names.append(NAME)

        #<pre>NAME=>EXPR</pre>
        jsmapper=JSArrowFunction(None,[*names],EXPR,isExpression=True)

        # If needed, we'll wrap that with:
        #<pre>NAME=>CONDITION</pre>
        if CONDITION:
            jsfilter=JSArrowFunction(None,[*names],CONDITION,isExpression=True)        
        else:
            jsfilter=JSNull()
        mappers.append(jsmapper)
        filters.append(jsfilter)

    invoked = JSCall(
            helper_func,
            [x.generators[0].iter,JSList(mappers),JSList(filters)])

    return invoked
