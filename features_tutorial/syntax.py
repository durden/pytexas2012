#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
__author__ = 'V James Powell <vpowell@gmail.com>'

# OUTLINE

# this handout addresses basic syntax for:
#  1. functional programmming
#  2. generators
#  3. comprehensions
#  4. decorators
#  5. context managers

# BASIC FUNCTIONAL PROGRAMMING

# references:
#   Wikipedia First-Class Functions
#     http://en.wikipedia.org/wiki/First-class_function
#   Functional Programming HOWTO
#     http://docs.python.org/howto/functional.html

# start with a simple function definition
def foo():
	return 'foo'

# this function defintion creates a name
#   which is bound to an object representing the function

# Python is a dynamic language, and this dynamism extends to all things,
#   including function definitions

# when the Python interpreter processes a function definition (started with
#   `def name(...):' syntax), it takes the following block of code, parses it
#   into an AST, compiles the result into a code object, and then wraps
#   the results in a function object
# then, it binds a reference to this function object to the name `foo'

# foo is just one name to refer to this block of code, and foo is a variable
#   like any other

# therefore, `foo` is now a name in our set of local variables
assert 'foo' in locals()

# `foo` is guaranteed to be an object
assert isinstance(foo, object)

# in fact, `foo` is an object with a special property: it can be
#   `called'
# therefore, we can refer to it abstractly as a callable
assert callable(foo)

# callable() is a function in __builtins__ that returns True/False
#   if its argument is a callable

# in Python 3, the preferred way to do this is to just check
#   if foo is an instance of the Callable abstract base class
try:
	from collections import Callable
except ImportError:
	# moved to collections.abc in Python 3
	try:
		from collections.abc import Callable
	except ImportError:
		Callable = type(foo)
assert isinstance(foo, Callable)

# any object that supports ...() can be called and is considered a callable

# this includes anonymous functions (lambda functions)
lambda_foo = lambda: None
assert callable(lambda_foo)

# it includes functions implemented in C
assert callable(len) and callable(callable) 

# and many other things...

# when we talk about basic functional programming, we mean treating functions
#   as first-class values
# that means we can pass them to functions as arguments
# that means we can return them from functions as return values
# that means we can treat them like any other variable

# at the REPL (interactive editor/read-eval-print-loop,) we
#   can use `help` and `dir` to inspect functions

# comment these out to see what they do
#assert help(foo)
#assert dir(foo)

# we can pass foo to a function as an argument

# `bar` takes a function (more strictly, a callable) as an argument
#   then returns a tuple with the results of the function invoked twice
def bar( func ):
	return func(), func()

def foo():
	return 'foo'

assert foo() == 'foo'
assert bar(foo) == ('foo', 'foo')

# note that there is a difference between
#   passing the FUNCTION as an argument and passing the VALUE
#   of the invoked function as an argument
try:
	assert foo() == 'foo'
	bar(foo()) # we called foo(), giving `foo`
	           # this is like calling: bar('foo')
except TypeError as e:
	# except the string `foo` is not a callable!
	print e

# since we can pass foo to a function as an argument
#   we can also return it from a function as a return value
def choose( pred, if_func, else_func ):
	if pred:
		return if_func
	return else_func

def foo():
	return 'foo'
def bar():
	return 'bar'

assert foo() == 'foo'
assert bar() == 'bar'
assert choose( True,  foo, bar ) == foo
assert choose( False, foo, bar ) == bar
assert choose( True,  foo, bar )() == foo() == 'foo'
assert choose( False, foo, bar )() == bar() == 'bar'

# we are allowed to define functions wherever we please,
#   and these functions will be constructed dynamically

# in this file, all of the functions I have defined so far
#   have been constructed as you loaded or imported the file

def choose( pred ):
	def foo():
		return 'foo'
	def bar():
		return 'bar'
	return foo if pred else bar
assert choose( True  )() == foo() == 'foo'
assert choose( False )() == bar() == 'bar'

# since we are constructing these functions dynamically,
#   they should represent distinct objects!

assert id(choose) == id(choose) # same object

x, y = choose(True), choose(True)
assert id(x) != id(y) # difference objects

# now, we can write wrapping functions, too

def choose( pred, if_func, else_func ):
	def wrap():
		return if_func if pred else else_func
	return wrap

assert choose( True,  foo, bar )()() == foo() == 'foo'
assert choose( False, foo, bar )()() == bar() == 'bar'

# or,

def repeat( n, func ):
	def wrap():
		rv = []
		for _ in range(n):
			rv.append( func() )
		return rv
	return wrap

assert repeat( 3, foo )() == ['foo', 'foo', 'foo']
assert repeat( 5, foo )() == ['foo', 'foo', 'foo', 'foo', 'foo']

# since functions are values, we can use them anywhere we would use
#   a value

# e.g., as elements in a dictionary
assert {0: foo, 1: bar}[ 0 ]() == 'foo'
assert {0: foo, 1: bar}[ 1 ]() == 'bar'

# pos and neg represent +/- unary operators
from operator import pos, neg

assert pos( 10) ==  10
assert pos(-10) == -10

assert neg( 10) == -10
assert neg(-10) ==  10

assert abs(10) == abs(-10) == 10

# use them as values in a dictionary
assert {'pos': pos, 'neg': neg, 'abs': abs}[ 'pos' ](-100) == -100
assert {'pos': pos, 'neg': neg, 'abs': abs}[ 'neg' ](-100) ==  100

# use them as keys in a dictionary
assert {pos: 'pos', neg: 'neg'}[ pos ] == 'pos'
assert {pos: 'pos', neg: 'neg'}[ neg ] == 'neg'

# GENERATORS

# references:
#   Python Wiki Generators
#     http://wiki.python.org/moin/Generators
#   PEP 255 Simple Generators
#     http://www.python.org/dev/peps/pep-0255
#   Coroutines via Enhanced Generators
#     http://www.python.org/dev/peps/pep-0342

# generator yield-syntax is very straight-forward
#   a generator that uses yield-syntax looks just like a function
#   except instead of returning a value, it uses the `yield`
#   keyword to yield elements
# at call-side, a generator looks like a function call that has returned
#   some iterable (like a list or tuple)

def yield_syntax():
	yield 1

i = 0
for x in yield_syntax():
	assert x == 1 # every value comes out 1
	i += 1
assert i == 1 # only one value ever comes out

# converted to a list:
assert list( yield_syntax() ) == [ 1 ]

# since yield just provides a value for the iterating code,
#   you can have multiple yield statements and they will
#   yield values in turn
def yield_syntax():
	yield 1
	yield 2
	yield 3
ys = yield_syntax()

assert next(ys) == 1 # next returns the next value in an iterator
assert next(ys) == 2
assert next(ys) == 3

try:
	assert next(ys)
except StopIteration as e:
	# there are only 3 values provided by the generator
	print e

# the values retrieved from a generator are computed as demanded
#   and are yielded as demanded

# the values are not pre-computed, and the past state of what
#   has been yielded is not stored anywhere

# since past values are never stored, a generator yields values
#   until exhaustion, where exhaustion is marked by a
#   StopIteration error being thrown

ys = yield_syntax()        # create an instance of the generator
assert list(ys) == [1,2,3]
assert list(ys) == []      # ys was exhausted by the above
assert list(ys) == []
ys = yield_syntax()        # create another instance
assert list(ys) == [1,2,3]

# you'll commonly see generators iterate over another iterable
def yield_syntax():
	yield 1
	for x in [1,2,3,4]:
		yield x
assert list(yield_syntax()) == [1,1,2,3,4]

# unlike a list, which has a strictly finite number of values
#   and stores every value, a generator does not have to have
#   a finite number of values or even a deterministic number
#   of values: the below generator yields a random number
#   of values and may not deterministically stop (if we never
#   see a 7!)
from random import randint
def yield_syntax():
	while True:
		x = randint(0,10)
		yield x
		if x == 7:
			break

# the following generator runs forever!
def yield_syntax():
	while True:
		yield 1

try:
	# be careful in uncommenting the following line:
	# assert list(yield_syntax())
	pass
except MemoryError as e:
	# if the line runs, the list it will try to
	#   construct will keep growing without bound
	#   and we will run out of memory!
	print e

# like a function, a generator can take an argument when it's
#   created

# this generator yields each element of the supplied
#   list in duplicate
def yield_syntax( my_list ):
	for x in my_list:
		yield x
		yield x

assert list( yield_syntax([1,2,3]) ) == [1,1,2,2,3,3]

# you can use `return` or `return None` to exit from the
#   generator instead of just letting execution reach
#   the end of the block

# this generator yields each element until it hit a seven
def yield_syntax( my_list ):
	for x in my_list:
		yield x
		if x == 7:
			return

assert list( yield_syntax([1,2,3,4,5,6,7,8]) ) == [1,2,3,4,5,6,7]

# in Python 2, a generator never returns a value,
#   so even though it looks like a function, it can
#   never return a non-None value
try:
	exec '''
def yield_syntax():
	yield 1
	return 1
	'''
except SyntaxError as e:
	# cannot return non-1 value in Python 2 generator
	print e

# in Python 3, the introduction of the `yield from` syntax
#   allows generators to return values

# the `yield` keyword can actually return a value
#   the value it returns represents a value that a
#   function outside of the generator can inject back into it
def yield_syntax( val = None ):
	val = yield val
	while True:
		val = yield val

ys = yield_syntax()
assert next(ys) is None # yields None forever
assert next(ys) is None
assert next(ys) is None

# we can send a value back into the generator with .send()
# .send() sends a value into the generator which
#   is returned from the yield statement
#   and itself returns the next value in the generator

# next( gen ) is the same as gen.next()
# gen.next() is the same as gen.send(None)

assert ys.send(12) == 12 # ys.send(12) sends 12 in
                         #   and pulls out the next value
assert next(ys) is None

# note the flow of execution
#   we must first `yield` a value before we
#   can capture something sent into the
#   generator from outside
# this meansthere's nowhere for a value to go before
#   we've yielded for the first time!

def gen( x = None ):
	while True:
		x = yield x # we must yield before
		            #   we capture the
		            #   value returned from
		            #   the yield statement
g = gen()
try:
	g.send(1)
except TypeError as e:
	# we cannot send a non-None value in
	#   before we have yielded the first value
	#   from the generator, because there's nowhere
	#   for it to go!
	print e

# just as we can send values into the generator
#   we can also send Exceptions into the generator!

# these exceptions are raised at the point of the
#   last executed yield statement

# like .send(), .throw() will raise an exeption
#   then return the next iterated value

def gen():
	while True:
		try:
			yield 1
		except TypeError:
			yield 'type error!'
g = gen()
try:
	g.throw( Exception('exception from outside') )
except Exception as e:
	# if we call throw on aa just-started generator
	#   we will raise the exception before execution
	#   begins, so there is no way to trap it
	print e

g = gen()
next(g)
assert g.throw( TypeError('exception from outside') ) == 'type error!'
try:
	g.throw( ValueError('exception from outside') )
except ValueError as e:
	# we raised a Value Error at the site of the yield statement
	#   as expected
	print e

# finally, we can also .close() a generator to stop it from yielding values
g = ( x for x in xrange(10) )
assert next(g) == 0
assert next(g) == 1
g.close()
try:
	next(g)
except StopIteration as e:
	# g is no longer active, as we have explicitly closed it
	print e

# TODO: learn about `yield from` syntax available in Python 3.3 and above

# COMPREHENSIONS

# references:
#   PEP 202 List Comprehensions
#     http://www.python.org/dev/peps/pep-0202
#   PEP 274 Dict Comprehensions
#     http://www.python.org/dev/peps/pep-0274
#   Guido van Rossum's The History of Python
#   From List Comprehensions to Generator Expressions
#     http://python-history.blogspot.com/2010/06/from-list-comprehensions-to-generator.html

# list comprehensions are merely convenient syntax for constructing
#   lists in a manner similar to the common mathematical syntax of
#   x | 1 < x < 5, x in Z
# the above syntax can be read:
#   "all of the values x such that x is strictly between 1 and 5
#    and x is in the set of integers"

# since we are constructing lists explicitly, the syntax in Python
#   is a bit more straight-forward
assert [ x   for x in (1,2,3) ] == [1,2,3]
assert [ x*2 for x in (1,2,3) ] == [2,4,6]

# we can add conditionals similar to the predicates in the
#   mathematical formulation above
assert [ x   for x in (1,2,3) if x%2 == 0           ] == [2]
assert [ x*2 for x in (1,2,3) if x%2 != 0 and x > 1 ] == [6]

# the target of the `in` clause can be any iterator
assert [ x for x in (1,2,3)                     ] == [1,2,3]
assert [ x for x in {1:'one',2:'two',3:'three'} ] == [1,2,3]
assert [ x for x in xrange(1,4)                 ] == [1,2,3]

# the expression in the `for` clause can be any
#   variable expression (just as with a standard for-loop)
# the expression for the iterated value can also be any
#   expression
assert [x+y for x,y in ((1,2),(3,4),(5,6))] == [3,7,11]

# because the syntax for creating values requires an expression,
#   it is relatively difficult to maintain state
# it is possible, but ugly & unadvisable
d = []
assert [(d.append(x),sum(d))[-1] for x in xrange(10)] == \
       [0,1,3,6,10,15,21,28,36,45]

# within the list comprehension, we can iterate over as many
#   iterables as we please
# multiple `for ... in` clauses result in iteration over the cartesian product
assert [(x,y) for x in xrange(2) for y in xrange(2)] == \
       [(0,0),(0,1),(1,0),(1,1)]

# `for ... in` clauses can reference the current value of iteration
#   variables in previous `for ... in` clauses
assert [(x,y) for x in xrange(2) for y in xrange(x,4)] == \
       [(0,0),(0,1),(0,2),(0,3),(1,1),(1,2),(1,3)]

# like for-loops, list comprehensions leak the state of their iteration
#   variable outside of the block's scope
for x in (100,200,300):
	pass
assert x == 300

[x for x in (100,200,300)]
assert x == 300

# sometimes, we want to calculate a value that does not reqiure
#   knowing intermediate values: it can be calculated one value at a time
assert sum([x for x in range(10)]) == (9*(9+1))//2 == 45

# we do not need to precompute the entire list to calculate its sum
# we can compute it one element at a time

# if we can take our list comprehension syntax and remove the surrounding
#   brackets, we're left with just our `... for ... in ...` syntax
# this is called a generator-expression
assert sum( x for x in range(10) ) == (9*(9+1))//2 == 45

# when creating a standalone generator-expression and saving it to
#   a variable, we must surround it with parenthesis
# when passing a generator-expression to a function, we can omit
#   the parenthesis if the generator expression is the only argument

def chain( xs = None, ys = None ):
	if xs:
		for x in xs:
			yield x
	if ys:
		for y in ys:
			yield y
assert list( chain([1,2,3],[1,2,3]) ) == [1,2,3,1,2,3]

# if it is the sole argument, we do not need to parenthesise the generator-
#   expression
assert list( chain(x for x in xrange(1,6)) ) == [1,2,3,4,5]

try:
	exec 'chain( x for x in xrange(1,6), y for y in xrange(1,6) )'
except SyntaxError as e:
	# we must parenthesise the generator-expressions if they are not
	#   the sole argument
	print e

assert list(chain( (x for x in xrange(1,6)), (y for y in xrange(1,6)) )) == \
       [1,2,3,4,5,1,2,3,4,5]

# the syntax of a generator expression is identical to that of
#   a list comprehension
gen = ( x for x in [1,2,3] )
assert list(gen) == [1,2,3]

gen = ( x*2 for x in [1,2,3] )
assert list(gen) == [2,4,6]

gen = ( (x,y) for x in xrange(2) for y in xrange(2) )
assert list(gen) == [(0,0),(0,1),(1,0),(1,1)]

gen = ( (x,y) for x in xrange(2) for y in xrange(x,4) )
assert list(gen) == [(0,0),(0,1),(0,2),(0,3),(1,1),(1,2),(1,3)]

# generator-expressions can reference other generator-expressions
gen1 = (  x**2    for x in xrange(3) )
assert list(gen1) == [0,1,4]

gen1 = (  x**2    for x in xrange(3) )
gen2 = (  x+2     for x in gen1      )
assert list(gen2) == [2,3,6]

gen1 = (  x**2    for x in xrange(3) )
gen2 = (  x+2     for x in gen1      )
gen3 = ( (x**2)+2 for x in xrange(3) )
assert list(gen3) == [2,3,6] == list(gen2)

# unlike the list comprehension, the generator-expression does not
#   leak the iteration variable into the enclosing scope
# this should make sense, since the generator does not precompute
#   values (so its execution context is independent of where it is defined)
del x
assert list(x for x in xrange(5)) == [0,1,2,3,4]
try:
	x
except NameError as e:
	# x does not exist in this scope
	# it exists only in the frame where the generator
	#   expression was evaluated, which is an execution frame we cannot
	#   access
	print e

# DECORATORS

# references:
#   PEP 318 Decorators for Functions and Methods
#     http://www.python.org/dev/peps/pep-0318
#   PEP 3129 Class Decorators
#     http://www.python.org/dev/peps/pep-3129

# decorators @-syntax allows the application of a function
#   to a function or a class and assignment of the return value
#   to the decorated name

def decorator( func ):
	return func

# the following two pieces of syntax should be semantically identical
def foo():
	return 'foo'
foo = decorator( foo ) # this is all @-syntax does

# identical to the above
@decorator
def foo():
	return 'foo'

# @-syntax calls the decorator with the following function
#   as its argument then assigns the function's name to the result

# this decorator does nothing:
#   it accepts a function and returns it
def decorator( func ):
	return func

# decorator `decorates` foo
@decorator
def foo():
	return 'foo'

# the decorator is a function that takes a function and returns a function
assert callable(decorator) and callable(foo) and\
       callable(decorator(foo))

# decorator does not wrap or modify foo's behaviour
assert foo() == 'foo'

# usually, a decorator introduces a new function which wraps
#   the original function

# this decorator wraps func in a new function that returns
#   a tuple containing the value of func called three times
def decorator( func ):
	def wrapper():
		return func(), func(), func()
	return wrapper

@decorator
def foo():
	return 'foo'

assert foo() == ('foo', 'foo', 'foo')

# a decorator is any function that takes a function and returns
#   a function

# the following is a user-defined class that can be called (a `functor' in
#   C++ terminology)
class Decorator( object ):
	def __call__( self, func ):
		def wrapper():
			return func(), func(), func()
		return wrapper

# this can be used as a decorator just as a regular function can
@Decorator()
def foo():
	return 'foo'

assert foo() == ('foo', 'foo', 'foo')

# a decorator of this form just constructs a function, wraps the original
#   function, and returns the wrapped result

# if we want to parameterise this, we might start with:
n = 5
def decorator( func ):
	def wrapper():
		rv = []
		for _ in xrange(n):
			rv.append( func() )
		return rv
	return wrapper

@decorator
def foo():
	return 'foo'

assert foo() == ['foo', 'foo', 'foo', 'foo', 'foo']

# @-syntax takes an expression that evalutes to a function that
#   accepts a function and returns a function
# there are some limitations (e.g., a lambda expression cannot
#   be used to construct an anonymous decorator

# the following is a function that constructs
#   a decorator
# the decorator() is identical to the one above
#   with the only addition being the outer layer that allows
#   us to capture the value of n
def repeater( n ):
	def decorator( func ):
		def wrapper():
			rv = []
			for _ in xrange(n):
				rv.append( func() )
			return rv
		return wrapper
	return decorator

@repeater(7)
def foo():
	return 'foo'

assert foo() == ['foo', 'foo', 'foo', 'foo', 'foo', 'foo', 'foo']

# just as the function decorators above take functions and return
#   functions, we can create a decorator that takes a class and returns a
#   class

# this decorator does nothing of note
def decorator( cls ):
	return cls

@decorator
class Foo( object ):
	pass

# this decorator adds a function to the class called bar
def decorator( cls ):
	def bar( self ):
		return 'bar'
	cls.bar = bar
	return cls

@decorator
class Foo( object ):
	pass

assert Foo().bar() == 'bar'

# CONTEXT MANAGERS

# references:
#   PEP 343 The "with" Statement
#     http://www.python.org/dev/peps/pep-0343

# context managers are useful for performing set up and tear down
#   like closing a database connection or a file automatically

# the open() function in __builtins__ is actually a context manager
#   that automatically closes the file once execution leaves the
#   block (either by running to completion or in the event of
#   an exception being raised)

filename = __file__
with open( filename ) as f:
	# find me!
	assert any('# find me!' in x for x in f.readlines())

# a context manager is simply some object that defines __enter__
#   and __exit__
# __enter__ is a method that takes no arguments and returns
#   the object that can be captured with the `as ...` clause
# __exit__ is a method that takes the type, value, and traceback
#   in the event an exception has been raised and execution
#   leaves the block
class contextmgr( object ):
	def __enter__( self ):
		print 'set up'
	def __exit__( self, type, value, traceback ):
		print 'tear down'

# prints:
#   set up
#   procesisng code
#   tear down
with contextmgr():
	print 'processing code'

# contextlib contains a very nice decorator named contextmanager

# this decorator can wrap any generator to turn it into a
#   context manager
# the wrapped generator must yield exactly once; the yielded
#   value is the value captured by the `as ...` clause
from contextlib import contextmanager
@contextmanager
def contextmgr():
	print 'set up'
	try:
		yield
	finally:
		print 'tear down'

# prints:
#   set up
#   procesisng code
#   tear down
with contextmgr():
	print 'processing code'

@contextmanager
def contextmgr():
	print 'set up'
	yield
	yield
	print 'tear down'

try:
	with contextmgr():
		print 'processing code'
except RuntimeError as e:
	# the wrapped generator must yield only once!
	print e
