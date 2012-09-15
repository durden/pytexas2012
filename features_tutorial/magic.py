#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# this handout goes through a few pieces of very non-magical
#   Python
# 1. callables
# 2. unpacking
# 3. decorators
# 4. iterables

# CALLABLES

# Python doesn't have functions so much as it 
#   has function-syntax, lambda-syntax, &c. and callables

# a callable is any object that responds to ()

def foo():
	pass

# foo is a callable, because it responds to ()
assert foo() == None

# we can check if a name is bound to a callable
#   using callable() in __builtins__
assert callable(foo)

# the callable to which the name foo is bound 
#   could have been declared in any of the following ways

# foo could have been created with function-syntax
def function_foo():
	return 'foo'

assert callable(function_foo)
assert function_foo() == 'foo'

# foo could have been created with lambda-syntax
lambda_foo = lambda: 'foo'

assert callable(lambda_foo)
assert lambda_foo() == 'foo'

# foo could be a generator created with yield-syntax
def generator_foo():
	yield 'foo'

assert callable(generator_foo)
assert next(generator_foo()) == 'foo'

# foo could have been new-style class, in which case
#   foo() would result in a new instance of the class foo
#   and would invoke the __new__ and __init__ mechanisms
# note that all objects of type `type' are callables
#   and they generally return new instances of objects of
#   the given type
class class_foo( object ):
	def __init__( self ):
		self.value = 'foo'

assert callable(class_foo)
assert class_foo().value == 'foo' 

# foo could be an object with a  __call__ method, similar to 
#  `functors' in C++
class Functor_Foo( object ):
	def __call__( self ):
		return 'foo'

functor_foo = Functor_Foo()
assert callable(functor_foo)
assert functor_foo() == 'foo'

# foo could have been a function implemented in C, &c. &c.

# behind the scenes, each syntax creates an object (PyObject)
#   and binds it to a name
# when the compiler sees the ...() syntax, it generally executes
#   the code attached to the __call__ member of that object
# this means that a function defined with function-syntax
#   is an object, too:
assert dir(function_foo)

# however, given how common function calls are, there are many
#   optimisations that speed things up behind the scenes

# because foo is an object, we can assign foo to a variable

def foo():
  return 'foo'

assert foo() == 'foo'

bar = foo
assert bar() == 'foo'

baz = foo
assert baz() == 'foo'

# foo, bar, and baz are names bound to the SAME object
assert id(foo) == id(bar) == id(baz)

# in fact, when you use function-syntax (def ...) you're just creating
#   a callable and then assigning it to the name you provided.

def foo():
	return 'foo'
def bar():
	return 'bar'

# foo and bar are bound to different functions
assert id(foo) != id(bar)
assert foo() == 'foo'
assert bar() == 'bar'

# but I can bind bar to the same object as foo
bar = foo
assert id(foo) == id(bar)
assert   foo() == bar() == 'foo'

# because we can bind functions to names, shis means we can pass functions to
#   functions as arguments

def foobar( func ):
	return func()

def foo():
	return 'foo'
def bar():
	return 'bar'

assert foo() == foobar( foo ) == 'foo'
assert bar() == foobar( bar ) == 'bar'

# we can use function-syntax to declare a function
#   anywhere, and all this does is create a callable
#   and assign it to a name.
# so we could write a function that takes a function
#   as an argument. This function creates a new
#   function and returns it.

def threetimes( func ):
	def wrapper():
		return func(), func(), func()
	return wrapper
def foo():
	return 'foo'

assert callable( threetimes )
assert callable( foo )

assert foo() == 'foo'

foo_thrice = threetimes( foo )
assert callable( foo_thrice )
assert foo_thrice() == ('foo','foo','foo')

# note that we can wrap foo_thrice one more time
foo_ninetimes = threetimes( threetimes( foo ) )
assert callable( foo_ninetimes )
# the return type is not 'foo' nine-times but
#   'foo' three times (first layer/application of threetimes())
#   and that result then three times (second layer of threetimes())
assert foo_ninetimes() == (('foo','foo','foo'),
                           ('foo','foo','foo'),
                           ('foo','foo','foo'))

# a decorator is just syntax to make this easier.
#   Decorator syntax is an @-sign, then the name of a 
#   function.

def threetimes( func ):
	def wrapper():
		return func(), func(), func()
	return wrapper

# the following two are identical

def manual_foo():
  return 'foo'
manual_foo = threetimes(foo) # returns a function from 
                             #   threetimes() then binds
                             #   this to the name manual_foo

@threetimes           # exact same as above:
def decorated_foo():  #   passes decorated_foo to threetimes()
	return 'foo'      #   and rebinds the name decorated_foo
                      #   to the return value of threetimes()

assert callable( manual_foo )
assert callable( decorated_foo )
assert manual_foo() == decorated_foo() == ('foo','foo','foo')

# that's all a decorator is:
#   1. a function that returns a function
#   2. @-syntax to use with
#       function-syntax for convenience
#         @decorator
#         def foo():
#           pass
#       is exactly equivalent to:
#         def foo():
#           pass
#         foo = decorator(foo)

# when the Python parser sees foo(), it translates this into
#   the bytecode CALL_FUNCTION
# there are also bytecodes CALL_FUNCTION_VAR, CALL_FUNCTION_KW, 
#   CALL_FUNCTION_VAR_KW that are used for function calls that do
#   tuple unpacking (VAR/*args) and dictionary unpacking (KW/**kwargs)

from contextlib import contextmanager
import sys
@contextmanager
def capture_print( stdout, stderr ):
	sys.stdout, sys.stderr, old = stdout, stderr, (sys.stdout, sys.stderr)
	try:
		yield sys.stdout, sys.stderr
	finally:
		sys.stdout, sys.stderr = old

from StringIO import StringIO
from dis import dis

def call_function():
	foo()

with capture_print( StringIO(), StringIO() ) as (buf,_):
	dis( call_function )
assert 'CALL_FUNCTION' in buf.getvalue()

def call_function_var( *args ):
	foo( *args )

with capture_print( StringIO(), StringIO() ) as (buf,_):
	dis( call_function_var )
assert 'CALL_FUNCTION_VAR' in buf.getvalue()

def call_function_kw( **kwargs ):
	foo( **kwargs )

with capture_print( StringIO(), StringIO() ) as (buf,_):
	dis( call_function_kw )
assert 'CALL_FUNCTION_KW' in buf.getvalue()

def call_function_var_kw( *args, **kwargs ):
	foo( *args, **kwargs )

with capture_print( StringIO(), StringIO() ) as (buf,_):
	dis( call_function_var_kw )
assert 'CALL_FUNCTION_VAR_KW' in buf.getvalue()

# there are many optimisations to speed up common cases,
#   but, in general, all of these end up in PyObject_Call

# this tells us that while Python has types for the different kinds of calls:

def foo():
	pass
from types import FunctionType
assert type(foo) == FunctionType

foo = lambda: None
from types import LambdaType
assert type(foo) == LambdaType

class Foo( object ):
	def foo( self ):
		pass
from types import MethodType
assert type(Foo().foo) == MethodType

# the interpreter actually operates in terms of objects with __call__ methods
#   (with the exception of C Functions and such)

# we can think of this as a form of duck-typing
# the Python interpreter doesn't really care whether a provided object
#   is actually a function or not: it merely cares whether that object
#   responds to a certain interface (the __call__ method)

# UNPACKINGS

# CALL_FUNCTION_VAR, CALL_FUNCTION_VAR, CALL_FUNCTION_VAR_KW
#   end up calling ext_do_call() which handles conversion
#   of *args and **kwargs arguments to tuples and dictionaries
#   respectively
# for *args, the parameter must be something that is convertable
#   to tuple via Pysequence_Tuple()
# this merely requires that the parameter be iterable
# any iterable should work
class Unpackable( object ):
	def __iter__( self ):
		self.iterable = (x for x in xrange(3))
		return self
	def next( self ):
		return next(self.iterable)

def foo( a, b, c ):
	return a, b, c

assert foo(*Unpackable()) == (0,1,2)

# for **kwargs, the parameter must be something that is convertible
#   to a dictionary via PyDict_Update()
# this requires that the parameter be a Mapping, which means it supports
#   PyMapping_Keys() and PyObject_GetItem() (which map to .keys() and
#   .__getitem__() respectively)
# of course, the keys of this object must be valid parameter names, otherwise
#   we'll see a TypeError

class KeywordUnpackable( object ):
	def keys( self ):
		return ('a','b','c')
	def __getitem__( self, key ):
		if key == 'a':
			return 0
		if key == 'b':
			return 1
		if key == 'c':
			return 2
		raise KeyError( 'key not in (%s)' % ', '.join(self.keys))

def foo( c, b, a ):
	return a, b, c

assert foo(**KeywordUnpackable()) == (0,1,2)

# DECORATORS

# this means that we could, for example, use something other than a 
#   def-syntax function as a decorator

# we could wrap a function in another object!
# the following passes the function to the __init__ method of
#   Decorator (which implicitly returns an instance of Decorator)
# since a Decorator object has __call__ defined, this
#   callable takes a callable and returns a callable: it is a valid
#   decorator
class Decorator( object ):
	def __init__( self, func ):
		print '__init__', func
		self.func = func
	def __call__( self, *args, **kwargs ):
		print '__call__', args, kwargs
		return self.func( *args, **kwargs ), self.func( *args, **kwargs )

@Decorator
def foo():
	return 'foo'

assert foo() == ('foo','foo')

# the following is an object with __call__ defined
#   here, it is not the value constructor that acts a a decorator
#   but the instance itself
class Decorator( object ):
	def __call__( self, func ):
		print '__call__', func 
		def wrapper( *args, **kwargs ):
			return func( *args, **kwargs ), func( *args, **kwargs )
		return wrapper

@Decorator()
def foo():
	return 'foo'

assert foo() == ('foo','foo')

# we could use a lambda as a decorator!
decorator = lambda f: lambda *a, **kw: (f(*a,**kw),f(*a,**kw))
@decorator
def foo():
	return 'foo'

assert foo() == ('foo','foo')

# we could even use a generator as a decorator!
def decorator( func ):
	yield func(), func()
	
@decorator
def foo():
	return 'foo'

# note that we don't call foo, since foo is 
#   now a generator, so instead of calling it
#   we use next() to retrieve values
assert next(foo) == ('foo','foo')

# ITERABLES

# when the Python compiler sees a for loop, it translates
#   this into the bytecodes GET_ITER/FOR_ITER (and JUMP_ABSOLUTE, &c.)

from StringIO import StringIO
from dis import dis

def for_loop():
	for x in y:
		pass
with capture_print( StringIO(), StringIO() ) as (buf, _):
	dis( for_loop )
assert 'GET_ITER' in buf.getvalue() 
assert 'FOR_ITER' in buf.getvalue() 

# GET_ITER ends up calling PyObject_GetIter
# FOR_ITER ends up calling ob_type->iternext()

# this tells us that a for loop operates on any object that
#   supports GetIter (which resolves to __iter__ for user-defined
#   classes)
	
# this means that we can create our own iterators by just creating
#   an object with __iter__ defined
class MyIter( object ):
	def __iter__( self ):
		return (x for x in xrange(10)) # this can return any iterable

for i,x in enumerate(MyIter()):
	assert i == x 

# similarly, FOR_ITER corresponds to next() in Python2 and __next__ in Python3

class MyIter( object ):
	def __iter__( self ):
		self.iter = (x for x in xrange(10))
		return self
	def next( self ):
		return next(self.iter)

for i,x in enumerate(MyIter()):
	assert i == x 
