#!/usr/bin/env python
import string
import sys

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
        raise Exception("+ requires 1+ args")
    return applyfloat(lambda a,b: a+b, args, local)

def f_diff(args, local):
    if len(args) < 2:
        raise Exception("- requires 2+ args")
    return applyfloat(lambda a,b: a-b, args, local)

def f_mul(args, local):
    if len(args) < 2:
        raise Exception("* requires 2+ args")
    return applyfloat(lambda a,b: a*b, args, local)

def f_div(args, local):
    if len(args) < 2:
        raise Exception("/ requires 2+ args")
    return applyfloat(lambda a,b: a/b, args, local)

def f_mod(args, local):
    if len(args) != 2:
        raise Exception("mod requires 2 args")
    a = runall(args, local)
    return int(args[0]) % int(args[1])

def f_pow(args, local):
    if len(args) != 2:
        raise Exception("pow requires 2 args")
    return float(args[0]) ** float(args[1])

def f_cat(args, local):
    if len(args) != 2:
        raise Exception("cat requires 2 args")
    try:
        args = runall(args, local)
        return args[0:1] + args[1]
    except TypeError:
        print args
        raise Exception("TypeError")

def f_first(args, local):
    if len(args) != 1:
        raise Exception("first requires 1 arg")
    lst = run(args[0], local)
    if len(lst) < 1:
        raise Exception("list passed to first must not be empty")
    return lst[0]

def f_rest(args, local):
    if len(args) != 1:
        raise Exception("rest requires 1 arg")
    lst = run(args[0], local)
    if len(lst) < 1:
        raise Exception("list passed to rest must not be empty")
    return lst[1:]

def f_last(args, local):
    if len(args) != 1:
        raise Exception("last requires 1 arg")
    lst = run(args[0], local)
    if len(lst) < 1:
        raise Exception("list passed to last must not be empty")
    return lst[-1]

def f_defun(args, local):
    if len(args) != 3:
        raise Exception("defun requires 3 args")
    if args[0] in primitives:
        raise Exception("cannot redefine built in function")
    fname = args[0]
    if type(fname) != str:
        raise Exception("function name must be a string - is " + str(type(fname)))
    fargs = args[1]
    for a in fargs:
        if type(a) != str:
            raise Exception("function args must be strings")
    fstatement = args[2]
    functions[fname] = [fargs, fstatement]
    return "defined function " + fname

def f_defvar(args, local):
    if len(args) != 2:
        raise Exception("defvar requires 2 args")
    vname = args[0]
    if type(vname) != str:
        raise Exception("variable name must be a string")
    variables[vname] = run(args[1], local)
    return "defined variable " + vname

def f_set(args, local):
    if len(args) != 2:
        raise Exception("set requires 2 args")
    vname = args[0]
    if type(vname) != str:
        raise Exception("variable name must be a string")
    if not vname in variables:
        raise Exception("cannot set nonexistant variable")
    value = run(args[1], local)
    variables[vname] = value
    return value

def f_let(args, local):
    if len(args) != 2:
        raise Exception("let requires 2 args")
    local = local.copy()
    for pair in args[0]:
        if type(pair) != list or len(pair) != 2:
            raise Exception("name value pairs must be 2 elements long")
        vname = pair[0]
        if type(vname) != str:
            raise Exception("variable name must be a string")
        value = run(pair[1], local)
        local[vname] = value
    return run(args[1], local)

def f_list(args, local):
    return runall(args, local)

def f_if(args, local):
    if len(args) != 3:
        raise Exception("if requires 3 args")
    if run(args[0], local):
        return run(args[1], local)
    else:
        return run(args[2], local)

def f_equal(args, local):
    if len(args) != 2:
        raise Exception("equal requires 2 args")
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
        raise Exception("< requires 2 args")
    args = runall(args, local)
    return args[0] < args[1]

def f_greater(args, local):
    if len(args) != 2:
        raise Exception("> requires 2 args")
    args = runall(args, local)
    return args[0] > args[1]

def f_or(args, local):
    if len(args) < 1:
        raise Exception("or requires 1+ args")
    for a in args:
        if run(a, local): return True
    return False

def f_not(args, local):
    if len(args) != 1:
        raise Exception("not requires 1 arg")
    if run(args[0], local):
        return True
    return False

def f_and(args, local):
    if len(args) < 1:
        raise Exception("and requires 1+ args")
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
    'and' : f_and
    }
functions = dict()
variables = dict()

def readWhitespace(text, i):
    size = len(text)
    while i < size and text[i].isspace():
        i += 1
    return i

def readList(text, i):
    size = len(text)
    tree = []
    if text[i] == '(':
        i += 1
        while text[i] != ')':
            i = readWhitespace(text, i)
            if text[i] == ')':
                break
            elif text[i] == '(':
                i, t = readList(text, i)
                tree.append(t)
            elif text[i] == '"':
                i, s = readString(text, i)
                tree.append(s)
            else:
                s = ''
                while i < size and  not (
                        text[i].isspace() or text[i] == ')'):
                    s += text[i]
                    i += 1
                tree.append(s)
        i += 1
    else:
        raise Exception("Bad starting character: " + text[i])
    return i, tree

def readString(text, i):
    size = len(text)
    last = '-'
    s = ''
    i += 1
    while i < size:
        if text[i] == '"' and last != '\\':
            break
        last = text[i]
        if text[i] != '\\':
            s += text[i]
        i += 1
    i += 1
    return i, s

def parse(text):
    size = len(text)
    trees = []
    i = readWhitespace(text, 0)
    while i < size:
        i, tree = readList(text, i)
        trees.append(tree)
        i = readWhitespace(text, i)
    return trees

def run(tree, local):
    if type(tree) == str:
        if tree in local:
            return local[tree]
        elif tree in variables:
            return variables[tree]
        elif tree in functions:
            return functions[tree]
    elif type(tree) == list:
        if len(tree) == 0: return []
        fn = tree[0]
        if fn in local:
            return runFunction(local[fn], tree[1:], local)
        elif fn in primitives:
            return primitives[fn](tree[1:], local)
        elif fn in functions:
            #print fn + " called with " + str(tree[1:]) + " in context " + str(local)
            return runFunction(functions[fn], tree[1:], local)
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


if len(sys.argv) > 1:
    fname = sys.argv[1]
    if fname == '-':
        text = sys.stdin.read()
    else:
        fin = open(fname, 'r')
        text = fin.read()
        fin.close()
    trees = parse(text)
    for tree in trees:
        print run(tree, dict())
