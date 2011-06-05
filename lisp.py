#!/usr/bin/env python
import string
import sys
import readline

#
# Helper functions:
#

def runall(args, local):
    return map(lambda x: run(x, local), args)

def applyfloat(f, args, local):
    return reduce(f, map(float, runall(args, local)))

#
# Primitive functions:
#

def f_sum(args, local):
    if len(args) < 1:
        raise SyntaxError("+ requires 1+ args")
    return applyfloat(lambda a,b: a+b, args, local)

def f_diff(args, local):
    if len(args) < 2:
        raise SyntaxError("- requires 2+ args")
    return applyfloat(lambda a,b: a-b, args, local)

def f_mul(args, local):
    if len(args) < 2:
        raise SyntaxError("* requires 2+ args")
    return applyfloat(lambda a,b: a*b, args, local)

def f_div(args, local):
    if len(args) < 2:
        raise SyntaxError("/ requires 2+ args")
    return applyfloat(lambda a,b: a/b, args, local)

def f_mod(args, local):
    if len(args) != 2:
        raise SyntaxError("mod requires 2 args")
    a = runall(args, local)
    return int(args[0]) % int(args[1])

def f_pow(args, local):
    if len(args) != 2:
        raise SyntaxError("pow requires 2 args")
    return float(args[0]) ** float(args[1])

def f_cat(args, local):
    if len(args) != 2:
        raise SyntaxError("cat requires 2 args")
    try:
        args = runall(args, local)
        if type(args[0]) == str and args[0] and args[0][0] == '"':
            return args[0][0:-1] + args[1][1:]
        else:
            return args[0] + args[1]
    except TypeError:
        print args
        raise SyntaxError("TypeError")

def f_first(args, local):
    if len(args) != 1:
        raise SyntaxError("first requires 1 arg")
    lst = run(args[0], local)
    if len(lst) < 1:
        raise SyntaxError("list passed to first must not be empty")
    if type(lst) == list:
        return lst[0]
    elif type(lst) == str and lst[0] == '"':
        return lst[1]

def f_rest(args, local):
    if len(args) != 1:
        raise SyntaxError("rest requires 1 arg")
    lst = run(args[0], local)
    if len(lst) < 1:
        raise SyntaxError("list passed to rest must not be empty")
    return lst[1:]

def f_last(args, local):
    if len(args) != 1:
        raise SyntaxError("last requires 1 arg")
    lst = run(args[0], local)
    if len(lst) < 1:
        raise SyntaxError("list passed to last must not be empty")
    return lst[-1]

def f_defun(args, local):
    if len(args) != 3:
        raise SyntaxError("defun requires 3 args")
    if args[0] in primitives:
        raise SyntaxError("cannot redefine built in function")
    fname = args[0]
    if type(fname) != str:
        raise SyntaxError("function name must be a string - is " + str(type(fname)))
    fargs = args[1]
    for a in fargs:
        if type(a) != str:
            raise SyntaxError("function args must be strings")
    fstatement = args[2]
    functions[fname] = [fargs, fstatement]
    return "defined function " + fname

def f_defmacro(args, local):
    if len(args) != 3:
        raise SyntaxError("defmacro requires 3 args")
    fname = args[0]
    if type(fname) != str:
        raise SyntaxError("macro nmae must be a string")
    farg = args[1]
    if type(farg) != str:
        raise SyntaxError("macro arg name must be a string")
    fstatement = args[2]
    macros[fname] = [farg, fstatement]
    return "defined macro " + fname

def f_defvar(args, local):
    if len(args) != 2:
        raise SyntaxError("defvar requires 2 args")
    vname = args[0]
    if type(vname) != str:
        raise SyntaxError("variable name must be a string")
    variables[vname] = run(args[1], local)
    return "defined variable " + vname

def f_set(args, local):
    if len(args) != 2:
        raise SyntaxError("set requires 2 args")
    vname = args[0]
    if type(vname) != str:
        raise SyntaxError("variable name must be a string")
    if not vname in variables:
        raise SyntaxError("cannot set nonexistant variable")
    value = run(args[1], local)
    variables[vname] = value
    return value

def f_let(args, local):
    if len(args) != 2:
        raise SyntaxError("let requires 2 args")
    local = local.copy()
    for pair in args[0]:
        if type(pair) != list or len(pair) != 2:
            raise SyntaxError("name value pairs must be 2 elements long")
        vname = pair[0]
        if type(vname) != str:
            raise SyntaxError("variable name must be a string")
        value = run(pair[1], local)
        local[vname] = value
    return run(args[1], local)

def f_list(args, local):
    return runall(args, local)

def f_if(args, local):
    if len(args) != 3:
        raise SyntaxError("if requires 3 args")
    if run(args[0], local):
        return run(args[1], local)
    else:
        return run(args[2], local)

def f_equal(args, local):
    if len(args) != 2:
        raise SyntaxError("equal requires 2 args")
    args = runall(args, local)
    t0 = type(args[0])
    t1 = type(args[1])
    if t0 == float: args[1] = float(args[1])
    elif t1 == float: args[0] = float(args[0])
    elif t0 == int: args[1] = int(args[1])
    elif t1 == int: args[0] = int(args[0])
    return args[0] == args[1]

def f_less(args, local):
    if len(args) != 2:
        raise SyntaxError("< requires 2 args")
    args = runall(args, local)
    return args[0] < args[1]

def f_greater(args, local):
    if len(args) != 2:
        raise SyntaxError("> requires 2 args")
    args = runall(args, local)
    return args[0] > args[1]

def f_or(args, local):
    if len(args) < 1:
        raise SyntaxError("or requires 1+ args")
    for a in args:
        if run(a, local): return True
    return False

def f_not(args, local):
    if len(args) != 1:
        raise SyntaxError("not requires 1 arg")
    if run(args[0], local):
        return True
    return False

def f_and(args, local):
    if len(args) < 1:
        raise SyntaxError("and requires 1+ args")
    for a in args:
        if not run(a, local): return False
    return True


primitives = {
    '+' : f_sum, 
    '-' : f_diff,
    '*' : f_mul,
    '/' : f_div,
    'mod' : f_mod,
    'pow' : f_pow,
    'cat' : f_cat,
    'first' : f_first,
    'rest' : f_rest,
    'last' : f_last,
    'defun' : f_defun,
    'defmacro' : f_defmacro,
    'defvar' : f_defvar,
    'set' : f_set,
    'let' : f_let,
    'list' : f_list,
    'if' : f_if,
    'equal' : f_equal,
    '<' : f_less,
    '>' : f_greater,
    'or' : f_or,
    'not' : f_not,
    'and' : f_and }

# 
# Logic to run program trees:
#

functions = dict()
macros = dict()
variables = dict()

def run(tree, local):
    if type(tree) == str:
        if tree in local:
            return local[tree]
        elif tree in variables:
            return variables[tree]
        elif tree in functions:
            return functions[tree]
        elif tree in macros:
            return macros[tree]
    elif type(tree) == list:
        if len(tree) == 0: return []
        fn = tree[0]
        # Not sure if this is a good idea...
        while type(fn) == list:
            fn = run(fn, local)
            tree[0:1] = fn
            fn = tree[0]
        if fn in primitives:
            return primitives[fn](tree[1:], local)
        elif fn in local:
            return runFunction(local[fn], tree[1:], local)
        elif fn in functions:
            return runFunction(functions[fn], tree[1:], local)
        elif fn in macros:
            return runMacro(macros[fn], tree[1:], local)
        else:
            raise Exception("unknown function " + fn)
    return tree

def runFunction(fun, args, local):
    args = map(lambda x: run(x,local), args)
    local = local.copy()
    # Set names
    for i in xrange(len(fun[0])):
        local[fun[0][i]] = args[i]
    return run(fun[1], local)

def runMacro(fun, args, local):
    if len(args) != 1:
        raise SyntaxError("Macros take a single tree. Was given " 
                + str(len(args)))
    local = local.copy()
    local[fun[0]] = args[0]
    return run(fun[1], local)


#
# Logic to read in programs:
#


class Machine:

    def __init__(self):
        self.stack = []
        self.current = None
        self.lastCh = None
        self.state = 0

    def startList(self):
        if self.state == 1:
            self.endName()
        if self.current is None:
            self.current = []
        else:
            self.stack.append(self.current)
            self.current = []

    def endList(self):
        if self.stack:
            p = self.stack.pop()
            p.append(self.current)
            self.current = p
        else:
            print run(self.current, dict())
            #print self.current
            self.current = None

    def startName(self, c):
        self.stack.append(self.current)
        self.current = c
        self.state = 1

    def endName(self):
        self.state = 0
        p = self.stack.pop()
        p.append(self.current)
        self.current = p

    def startString(self):
        self.stack.append(self.current)
        self.current = '"'
        self.state = 2

    def endString(self):
        p  = self.stack.pop()
        p.append(self.current + '"')
        self.current = p
        self.state = 0
        self.lastCh = None

    def addLine(self, line):
        line = self.readLine(str.rstrip(line))
        for c in line:
            if self.state == 0:
                if c == '(':
                    self.startList()
                elif c == ')':
                    self.endList()
                elif c == '"':
                    if self.current is None:
                        raise SyntaxError("Start of string outside of list")
                    self.startString()
                elif not c.isspace():
                    if self.current is None:
                        raise SyntaxError("Start of name outside of list")
                    self.startName(c)
            elif self.state == 1:
                if c == ')':
                    self.endName()
                    self.endList()
                elif c.isspace():
                    self.endName()
                else:
                    self.current += c
            elif self.state == 2:
                if c == '"' and self.lastCh != '//':
                    self.endString()
                else:
                    self.current += c
                    self.lastCh = c
        if self.state == 1:
            self.endName()


    def readLine(self, line):
        for c in line:
            yield c

def main():
    m = Machine()
    if len(sys.argv) > 1:
        # Read from file
        fin = open(sys.argv[1], 'r')
        for line in fin:
            try:
                m.addLine(line)
            except SyntaxError as e:
                print 'Syntax error: ' + str(e)
        fin.close()
    else:
        # interactive session
        while 1:
            try:
                line = raw_input('> ') + '\n'
            except:
                print ''
                break
            try:
                m.addLine(line)
            except SyntaxError as e:
                print 'Syntax error: ' + str(e)

if __name__ == '__main__':
    main()

