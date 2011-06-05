Toy LISP
========

This is a toy implementation of lisp, written in python, just for fun.

### use:

* run 

    ./lisp.py

  to get the interactive interpreter (which stops working after the first
  error...)

* run

    ./lisp.py filename

  to run the program in the file.

* run

    cat file1 fil2 file 3 | ./lisp.py

  to run a multi-file program.


Syntax
------

This uses the standard lisp syntax, like this:

    (print 
        (+ 1 2
           (* 2 3)))
    (defun f (x) 
        (if (> x 0)
            (f (- x 10))
            (0)))
    (list 1 2 3)
    (defvar x (list 4 5 6))

etc.

### Built-in functions:
* Math: +, -, *, /, %, and pow
* List: cat, first, rest, last, list
* Functions and variables: defun, defmacro, defvar, set, let
* Logic: equal, >, <, or, not, and
* Output: print
* Control flow: if, do, while

