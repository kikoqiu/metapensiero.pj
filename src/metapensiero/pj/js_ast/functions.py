# -*- coding: utf-8 -*-
# :Project:   metapensiero.pj -- functions
# :Created:   gio 08 feb 2018 02:29:14 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Alberto Berti
#

from .blocks import JSBlock
from ..processor.util import delimited


class JSFunction(JSBlock):

    begin = 'function '
    bet_args_n_body = ''

    def fargs(self, args, acc=None, kwargs=None,arg_init=None):
        result = []
        result.append('(')
        js_args = args.copy()        
        
        if (not acc):
            if kwargs:
                acc='..._arg_acc'
        if acc:
            js_args.append(acc)
        
        if kwargs:
            extra_args=[]
            extra_args.append(self.part('[',acc,'],'))
            extra_args.append(self.part('{', *delimited(', ', kwargs), '},'))
            arg_init+=['var [',*extra_args,']=_pj.ext_acc(',acc,')']

        delimited(', ', js_args, dest=result)

        result.append(') ')
        return result

    def emit(self, name, args, body, acc=None, kwargs=None):
        line = [self.begin]
        if name is not None:
            line.append(name)
        arg_init=[]
        line += self.fargs(args, acc, kwargs,arg_init)
        line += self.bet_args_n_body
        line += ['{']        
        yield self.line(line, name=str(name))
        if arg_init:
            yield self.line(arg_init, indent=True, delim=True)
        yield from self.lines(body, indent=True, delim=True)
        yield self.line('}')


class JSAsyncFunction(JSFunction):

    begin = 'async function '


class JSGenFunction(JSFunction):

    begin = 'function* '


class JSArrowFunction(JSFunction):

    begin = ''
    bet_args_n_body = '=> '

    def emit(self, name, args, body, acc=None, kwargs=None, isExpression=None):
        if name:
            # TODO: split this into an assignment + arrow function
            line = [name, ' = ']
        else:
            line = []
        arg_init=[]
        line += self.fargs(args, acc, kwargs,arg_init)
        line += self.bet_args_n_body
        if isExpression:
            assert not arg_init
            line+=[body]
            yield self.part(*line)
        else:
            line += ['{']            
            yield self.line(line)
            if arg_init:
                yield self.line(arg_init)
            yield from self.lines(body, indent=True, delim=True)
            if name:
                yield self.line('}', delim=True)
            else:
                yield self.part('}')

