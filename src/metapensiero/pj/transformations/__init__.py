# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj
# :Created:  gio 09 mar 2017 19:43:11 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

import ast
import logging

from metapensiero.pj.js_ast.operators import JSRest

from ..js_ast import JSKeySubscript, JSStr, TargetNode

logger = logging.getLogger(__name__)


def _normalize_name(n):
    if n.startswith('d_'):
        n = n.replace('d_', '$')
    elif n.startswith('dd_'):
        n = n.replace('dd_', '$$')
    if n in ['new','catch']:
        n='_esc_'+n
    # allow to reference names that are Python's keywords by appending
    # a dash to them
    #elif not n.startswith('_') and n.endswith('_'):
    #    n = n[:-1]
    return n

attribute_map={'__name__':'name'}
def _normalize_attribute_name(n):
    if n in attribute_map:
        return attribute_map[n]
    return _normalize_name(n)

def _normalize_dict_keys(transformer, keys):
    res = []
    for key in keys:
        if isinstance(key, str):
            key = ast.Str(key)
        elif isinstance(key, JSStr):
            key = ast.Str(key.args[0])
        if not isinstance(key, ast.Str) and not isinstance(key,JSRest):
            if transformer.enable_es6:
                key = JSKeySubscript(key)
            else:
                if isinstance(key, ast.AST):
                    py_node = key
                elif isinstance(key, TargetNode) and key.py_node is not None:
                    py_node = key.py_node
                else:
                    raise ValueError('Value of type %r cannot '
                                     'be use as key' % type(key))
                transformer.unsupported(py_node, True, 'Value of type %r cannot '
                                        'be use as key' % type(key))
        res.append(key)
    return res
