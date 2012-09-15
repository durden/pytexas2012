#!/usr/bin/env
# vim: set fileencoding=utf-8 :

# this handout delves into the motivation behind the use of these
#   features with examples
# 1. functional programming constructs
# 2. comprehensions, generators & generator expressions
# 3. decorators
# 4. context managers

# FUNCTIONAL PROGRAMMING

# Python is a functional programming language to the extent that
#   functions are first class values
# some argue that a functional programming language should have
#   mechanisms for managing purity and state, and Python lacks
#   explicit focus on this (though writing stateless, pure code
#   is made easy to do using generators and contextmanagers)
# however, first class functions are enough for Python to allow
#   many constructs that would be novel in a C, C++, VBA, or Java programme

# the benefits of a more functioanal approach to programming are 
#   generally very contextual; as a result, the following examples
#   should not be seen as constructs your code MUST use
#   but rather techniques that you can employ when looking for
#   ways to improve code quality

# imagine a function with some modality triggered by its inputs
#   i.e., a function where a parameter puts it into some mode,
#   changes some fundamental behaviour of the function

# in older, static languages, this modality would be triggered
#   by means of conditionals in the function body and some ad-hoc typing
#   on the formal parameters
from sqlite3 import connect
from contextlib import closing
def write_data( employees, dest=0 ):
	if source not in (0,1):
		raise ValueError( 'dest must be 0 or 1' )
	if source == 0:
		with open('source.csv', 'w') as f:
			for e in employees:
				f.write( ','.join(e) )
	elif source == 1:
		with connectioncontext('source.db') as conn, \
		       cursorcontext(conn) as cur:
			insert = 'INSERT INTO employees VALUES (?, ?, ?)'
			for e in employees:
				cur.execute( insert, e )
		
# this code is sub-optimal, as the user has no indication
#   from the outset what the valid domain of `source` is, nor is it
#   very obvious which source matches to which code number

# we could improve the code as follows:
from sqlite3 import connect
from contextlib import closing
def write_data( employees, dest='file' ):
	if source not in('file','database'):
		raise ValueError( 'dest must be 0 or 1' )
	if source == 'file':
		with open('source.csv', 'w') as f:
			for e in employees:
				f.write( ','.join(e) )
	elif source == 'database':
		with connectioncontext('source.db') as conn, \
		       cursorcontext(conn) as cur:
			insert = 'INSERT INTO employees VALUES (?, ?, ?)'
			for e in employees:
				cur.execute( insert, e )


# or, alternatively, using singleton objects instead of strings:
FILE, DATABASE = object(), object()
from sqlite3 import connect
from contextlib import closing
def write_data( employees, dest=FILE ):
	if source not in(FILE,DATABASE):
		raise ValueError( 'dest must be 0 or 1' )
	if source is FILE:
		with open('source.csv', 'w') as f:
			for e in employees:
				f.write( ','.join(e) )
	elif source is DATABASE:
		with connectioncontext('source.db') as conn, \
		       cursorcontext(conn) as cur:
			insert = 'INSERT INTO employees VALUES (?, ?, ?)'
			for e in employees:
				cur.execute( insert, e )

# note: the use of singleton objects doesn't necessarily gain us any
#   efficiency even though `is` is a pointer comparison and `==` is
#   a richer equality comparison
# this is because short strings in Python are interned, and interned
#   strings are also checked on pointer-equality

# neither of these two functions are much better, as in neither case
#   is the user guided toward providing only valid parameters
# additionally, the function has now encoded some modality that
#   may be beneficial to have at the calling end

# however, since Python allows functions to be passed as arguments, we
#   could rewrite the above as follows
def write_data( employees, write ):
	for e in employees:
		write( e )
def flatfile( f ):
	return lambda e: f.write( ','.join(e) )
def database( c ):
	insert = 'INSERT INTO employees VALUES (?,?,?)'
	return lambda e: c.execute(insert , e )

# to use:

# with open('source.csv', 'w') as f:
#   write_data( employees, flatfile(f) )
# with connectioncontext('source.db') as conn, \
#        cursorcontext(conn) as cur:
#   write_data( employees, database(cur) ) 

# the above is less indented, with better defined parameters (write is
#   now some function that just takes employee objects and does something
#   with them) 
# the code is shorter, easier to read, and more extensible
#   as later users could add their own write functions

# similarly, we can use first class functions to return richer
#   return values

# we might start with something like the below
def can_fire( employee1, employee2 ):
	if employee1 == employee2:
		return 0
	if employee1.role == 'ceo':
		return 1
	if employee1.role == 'manager' and employee2.role != 'manager':
		return 1
	return 0

# the use of 0/1 as True/False is correct and not uncommon
#   but we have access to richer types
def can_fire( employee1, employee2 ):
	if employee1 == employee2:
		return False
	if employee1.role == 'ceo':
		return True
	if employee1.role == 'manager' and employee2.role != 'manager':
		return True
	return False

# however, we could write this not only to take a function 
#  that extracts some core logic into a central place but 
#  also returns a function instead just True/False
def fire( employee1, employee2 ):
	def fire( employee ):
		employee.terminated = True
	def noop( employee ):
		pass
	if employee1 == employee2:
		return noop
	if employee1.role == 'ceo':
		return fire
	if employee1.role == 'manager' and employee2.role != 'manager':
		return fire
	return noop

# usage would then be like:
#   fire( ceo, peon )( peon )
# instead of:
#   if can_fire( ceo, peon ):
#     peon.terminated = True
#   else:
#     pass

# Python lacks a switch statement as you would find in C, C++, Java, and VBA
# however, we can get around this by using a dictionary and first class
#   functions
def reward( employee ):
	if employee.role == 'ceo':
		employee.salary += 1000000
	if employee.role == 'division director':
		employee.salary += 120000
	if employee.role == 'associate director':
		employee.salary += 90000
	if employee.role == 'senior manager':
		employee.salary += 45000
	if employee.role == 'manager':
		employee.salary += 20000
	if employee.role == 'peon':
		pat_on_back( employee )

# we can rewrite this as follows
def reward( employee ):
	def pay_raise( amount ):
		def add_salary( employee ):
			employee.salary += amount
		return add_salary
	incentives = { 'ceo'               : pay_raise(1000000),
	               'division director' : pay_raise(120000),
	               'associate director': pay_raise(90000),
	               'senior manager'    : pay_raise(45000),
	               'manager'           : pay_raise(20000),
	               'peon'              : pat_on_back }
	incentives[ employee.role ]( employee )

# we can also use functions for basic code reduction tasks
def process( data ):
	data = read( data )
	data = parse( data )
	data = overlay( data )
	data = process( data )
	data = finalise( data )
	return data

# we can easily reduce this to:
def process( data ):
	for phase in (read,parse,overlay,process,finalise):
		data = phase(data)
	return data

# COMPREHENSIONS

# the value of list comprehensions should be fairly obvious:
#   they enable us to quickly construct lists that would either
#   require long for-loops to construct
evens = []
for x in xrange(10):
	if x % 2 == 0:
		evens.append( x )
assert evens == [0,2,4,6,8]

assert [x for x in xrange(10) if x%2 == 0] == [0,2,4,6,8]

# similarly, complex code that involves multiple levels of conditionals
#   can be flattened into code that operates on a sequence of
#   list comprehensions or generators

# we want even numbers that are perfect squares
#   or odd numbers that are multiples of 5
nums = set()
for x in xrange(100):
	if x%2 == 0 and int(x**.5)**2 == x:
		nums.add(x)
	elif x%2 != 0 and x%5 == 0:
		nums.add(x)

assert nums == ({x for x in xrange(100) if x%2 == 0 and int(x**.5)**2 == x} | 
                {x for x in xrange(100) if x%2 != 0 and x%5 == 0} )

# or, take all the numbers in the list,
#  squaring multiples of three
#    then dividing by two if even
#    or adding one if odd
#  cubing multiples of five
#  ignoring multiples of six
#  zeroing multiples of seven
nums = set()
for x in xrange(100):
	if x % 6 == 0:
		pass
	else:
		if x % 3 == 0:
			if (x**2) % 2 == 0:
				nums.add( x**2 // 2 )
			else:
				nums.add( x**2 + 1)	
		if x % 5 == 0:
			nums.add( x**3 )
		if x % 7:
			nums.add( 0 )

assert nums == {0, 64000, 3970, 512000, 15625, 10, 7570, 4762,
                857375, 6562, 2602, 3375, 3250, 442, 9802, 8000,
                274625, 1090, 125000, 8650, 82, 343000, 730, 226,
                166375, 1000, 2026, 614125, 1522, 421875, 91125,
                5626, 42875, 125}

# let's see how we can flatten this using a sequence
#   of set comprehensions

nums = xrange(100)                            # start with [0,100)
nums =   { x      for x in nums if x%6 != 0 } # filter out multiples of six

threes = { (x**2) for x in nums if x%3 == 0 } # square multiples of three
threes = { (x//2 if x%2==0 else x+1)          #   //2 if even, +1 if odd
                  for x in threes }
fives  = { (x**3) for x in nums if x%5 == 0 } # cube multiples of five
sevens = { 0      for x in nums if x%7 == 0 } # zero multiples of seven

nums = threes | fives | sevens                # combine

assert nums == {0, 64000, 3970, 512000, 15625, 10, 7570, 4762,
                857375, 6562, 2602, 3375, 3250, 442, 9802, 8000,
                274625, 1090, 125000, 8650, 82, 343000, 730, 226,
                166375, 1000, 2026, 614125, 1522, 421875, 91125,
                5626, 42875, 125}

# the following code is very natural for a C++, C, or Java programmer to write
i = 0
for x in [1,2,3,7,11,19,43,67,163]:
	print '%d: %d' % (i, x)
	i += 1

i = 0
for x in [23,31,59,83,107,139,211]:
	print '%d: %d' % (i,x)
	i += 1

# however, you can see that we are repeating ourselves,
#   and we are maintaining some state manually:
#   we are maintaining the state of the iteration in
#   the variable `i`

# GENERATORS

# in __builtins__, we have a generator that allows us
#   to extract this logic and keep it in one place:

# enumerate()

# enumerate() takes an iterable and yields pairs of
#   (i,x) where i is the current index of the iterable
#   and x is the next value from the iterable

for i,x in enumerate([1,2,3,7,11,19,43,67,163]):
	print '%d: %d' % (i, x)

for i,x in enumerate([23,31,59,83,107,139,211]):
	print '%d: %d' % (i,x)

# this is one very good use of a generator:
#   it allows us to extract code that operates
#   on some sequence by wrapping the sequence in
#   a generator
# you can easily imagine that if our for loop became
#   longer or more detailed, it would become very easy
#   to misplace the line `i += 1`
# and, if we think about it, the maintenance of this
#   loop state isn't really part of our business logic
# our goal is to just print indices and numbers, and
#   the use of enumerate() allows us cleanly separate
#   the code that accomplishes this goal and the code
#   that merely provides us with the values to be printed

# we could easily use a generator to simplify code
#   that maintains some per-loop state: to extract the
#   processing to a single generator and shorten
#   and simplify our loops

# e.g., 
for x in xrange(10):
	x_sq = x**2
	print '%d^2 = %d' % (x, x_sq)

def squares( iterable ):
	for x in iterable:
		yield x, x**2

for x, x_sq in squares(xrange(10)):
	print '%d^2 = %d' % (x, x_sq)

# a more complex example:
# say we have a string that contains letters of mixed case
# we want to find the first instance of a substring where you have
#   three lowercase letters, then an uppercase letter, then a lowercase
#   letter

def find( s ):
	for idx in xrange(len(s) - 6):
		check = s[idx:idx+7] 
		if check[ :3].islower() and \
		   check[4: ].islower() and \
		   check[3:4].isupper():
			return check

s = 'jfjheNeKdlwoqjasJjasjDfk'
#                 ---=---
assert find(s) == 'jasJjas'

# but, the for loop above obscures our check by
#   spending a line to process the substrings
# like with the use of enumerate(), we should be able
#   to extract maintenance of loop state into a generator
# in this case, we want a generator that gives us subsets
#   of seven values
from itertools import tee, izip
def pairwise( iterable, n ):
	iterables = tee( iterable, n )      # create n copies of the iterable
	for i,it in enumerate(iterables):   # for the nth copy of the iterable
		for _ in xrange( i ):           #   advance it n values
			next( it )                  # e.g., the 0th iterable advanced 0
			                            #       the 1st iterable advances 1
	return izip( *iterables )           # take these staggered iterables
	                                    #   and zip them together
	                                    # i.e., return tuples of the first
	                                    #   elements from each, the second
	                                    #   elements from each, &c.

def find( s ):
	for substr in map(lambda x: ''.join(x), pairwise( s, 7 )):
		if substr[ :3].islower() and \
		   substr[4: ].islower() and \
		   substr[3:4].isupper():
			return substr

assert find(s) == 'jasJjas'

# or, more simply:
from itertools import imap
def find( s ):
	substrings = imap(lambda x: ''.join(x),pairwise(s,7))
	match = lambda substr: substr[ :3].islower() and \
	                       substr[4: ].islower() and \
	                       substr[3:4].isupper()
	return next( (x for x in substrings if match(x)), None ) # None is the
	                                                         #   default retval

assert find(s) == 'jasJjas'

# here, we have reduced our find() function so that there is a better
#   ratio of lines of code for maintenance and lines of code for
#   performing our business logic
# additionally, we now have a function pairwise() that can be used
#   to solve other, similar problems:
# say we have a sorted list that contains numbers and we want to
#   print it out as a set of ranges
# e.g.,
# to_ranges( [1,2,3,5,10,11,12,17] ) ->
#   1-3, 5, 10-12, 17

# this generator yields contiguous 
#   subsets of a given iterable
def contiguous( iterable ):
	buffer = []                         # start with an empty buffer
	for x,y in pairwise( iterable, 2 ): # look at the elements pairwise
		buffer.append( x )              # put the element into the buffer
		if (y-x) > 1:                   # if the next element is a jump
			yield buffer                #   yield the buffer and reset
			buffer = []
	yield buffer + [y]                  # yield whatever is left over

assert list(contiguous([1,2,3,5,10,11,12,17])) == \
       [[1,2,3],[5],[10,11,12],[17]]

def to_ranges( iterable ):
	for subset in contiguous( iterable ):
		yield '%d' % subset[0] \
		       if len(subset) == 1 else \
		       '%d-%d' % (subset[0], subset[-1])

assert list(to_ranges([1,2,3,5,10,11,12,17])) == \
       ['1-3','5','10-12','17']

# itertools includes a number of very helpful generators
#   for helping us transform our iterables
# here's a brief overview of some of the more useful ones

# itertools.imap
# itertools.izip
# itertools.ifilter

# itertools.{imap,izip,ifilter} are variants of
#   __builtins__.{imap,izip,ifilter} that return iterators instead of
#   materialised lists
# in Python 3, all __builtins__ that operate on sequence types
#   return iterators, so the distinction between map and imap no longer exists

# zip( *iterables ), as we know, takes pairwise elements from 
#   the provided iterables
def my_zip( *iterables ):
	iterables = [iter(x) for x in iterables]
	rv = []
	while True:
		try:
			val = [next(x) for x in iterables]
			rv.append( tuple(val) )
		except StopIteration:
			return rv

from itertools import izip
assert my_zip(    xrange(10) ,xrange(10) )  == \
       zip(       xrange(10) ,xrange(10) )  == \
       list(izip( xrange(10), xrange(10) )) == \
       [(0,0),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9)]

from string import ascii_lowercase
assert my_zip(    xrange(5), ascii_lowercase )  == \
       zip(       xrange(5), ascii_lowercase )  == \
       list(izip( xrange(5), ascii_lowercase )) == \
       [(0,'a'),(1,'b'),(2,'c'),(3,'d'),(4,'e')]

# map( func, iterable ), as we know, applies the function to every
#   element of the iterable and returns a list of the results
# map( func, *iterables ), follows the same pattern, but applies
#   the function to each pair of elements from zip(*iterables)
def my_map( func, *iterables ):
	rv = []
	for elements in zip(*iterables):
		rv.append( func(*elements) )
	return rv

from itertools import imap
assert my_map(    lambda x: x+2, xrange(10))  == \
       map(       lambda x: x+2, xrange(10))  == \
       list(imap( lambda x: x+2, xrange(10))) == \
       [2,3,4,5,6,7,8,9,10,11]

assert my_map(    lambda x,y: x**y, xrange(10),xrange(10))  == \
       map(       lambda x,y: x**y, xrange(10),xrange(10))  == \
       list(imap( lambda x,y: x**y, xrange(10),xrange(10))) == \
       [1, 1, 4, 27, 256, 3125, 46656, 823543, 16777216, 387420489]

# filter( pred or None, iterable ), as we know, takes a function (`predicate`)
#   and an iterable and returns elements of that iterable for which the
#   predicate is True
def my_filter( pred, iterable ):
	pred = bool if pred is None else pred
	rv = []
	for element in iterable:
		if pred( element ):
			rv.append( element )
	return rv

iseven = lambda x: x % 2 == 0
isodd  = lambda x: x % 2 != 0

from itertools import ifilter
assert my_filter(    iseven, xrange(10) )  == \
       filter(       iseven, xrange(10) )  == \
       list(ifilter( iseven, xrange(10) )) == \
       [0, 2, 4, 6, 8]
assert my_filter(    isodd, xrange(10) )  == \
       filter(       isodd, xrange(10) )  == \
       list(ifilter( isodd, xrange(10) )) == \
       [1, 3, 5, 7, 9]

assert my_filter(    None, [False,True,0,1,0.0,1.0,'','a',[],[0],{},{0}])  == \
       filter(       None, [False,True,0,1,0.0,1.0,'','a',[],[0],{},{0}])  == \
       list(ifilter( None, [False,True,0,1,0.0,1.0,'','a',[],[0],{},{0}])) == \
       [True,1,1.0,'a',[0],{0}]

# itertools.tee

# tee is like the coreutils command line utility, `tee`
#   take an iterable (stream) and return n independent iterables
# this is useful with generators, since yielding values from a generator
#   will exhaust the generator

gen = (x for x in xrange(10))
assert list(gen) == list(xrange(10)) == [0,1,2,3,4,5,6,7,8,9]
assert list(gen) == [] # exhausted

gen = (x for x in xrange(10))

from itertools import tee
gen1, gen2 = tee(gen,2)
assert list(gen1) == list(xrange(10)) == [0,1,2,3,4,5,6,7,8,9]
assert list(gen1) == [] # exhausted
# but gen2 is independent of gen1!
assert list(gen2) == list(xrange(10)) == [0,1,2,3,4,5,6,7,8,9]
assert list(gen2) == [] # exhausted

# itertools.groupby

# groupby takes a sorted iterable and forms groups (similar to the SQL
#   GROUP BY command)

from collections import namedtuple
Employee = namedtuple( 'Employee', 'name position salary' )
employees = ( Employee('janet',    'manager', 200000),
              Employee('john',     'manager', 500000),
              Employee('jim',      'peon',     65000),
              Employee('patricia', 'manager', 300000), )

# sort by position
# this is a necessary first step before using groupby()
# groupby will create groups only when the key's value changes
#   similar to how the command line utility `uniq` works
# this allows groupby to operate on infinite iterables and
#   iterables that we do not want to materialise
employees = list(sorted(employees, key=lambda e: e.position))

# group by position

# groupby returns an iterable of which each element is 
#   the key value and another iterable which contains all of the elements
# as a consequence, we have to do a little bit of work to materialise
#   the results of groupby() into something we can check
from itertools import groupby
assert [(k,set(v)) for k,v in groupby( employees, lambda e: e.position )] == \
       [('manager', {Employee('janet',    'manager', 200000),
                     Employee('john',     'manager', 500000),
                     Employee('patricia', 'manager', 300000)} ),
        ('peon',    {Employee('jim',      'peon',     65000)} )]

# itertools.product

# product(*iterables, repeat) gives the cartesian product of the provided
#   iterables
# the repeat parameter allows us to easily compute the cartesian product
#   of an iterable and itself
from itertools import product
assert list(product(xrange(3),'abcd')) == \
       [(0,'a'),(0,'b'),(0,'c'),(0,'d'),
        (1,'a'),(1,'b'),(1,'c'),(1,'d'), 
        (2,'a'),(2,'b'),(2,'c'),(2,'d')]

assert list(product(xrange(3),repeat=2)) == \
       [(a,b) for a in xrange(3) for b in xrange(3)] == \
       [(0,0),(0,1),(0,2),
        (1,0),(1,1),(1,2),
        (2,0),(2,1),(2,2)]

# itertools.combinations
# itertools.combinations_with_replacement
# itertools.permutations

# combinations, combinations_with_replacement, and permutations
#   provide possible orderings for an iterable
from itertools import combinations
assert list(combinations('abcd',2)) == \
       [('a','b'),('a','c'),('a','d'),('b','c'),('b','d'),('c','d')]

from itertools import combinations_with_replacement
assert list(combinations_with_replacement('abcd',2)) == \
       [('a','a'),('a','b'),('a','c'),('a','d'),
        ('b','b'),('b','c'),('b','d'),
        ('c','c'),('c','d'),
        ('d','d')]

from itertools import permutations
assert list(''.join(x) for x in permutations('abcd')) == \
       ['abcd', 'abdc', 'acbd', 'acdb', 'adbc', 'adcb',
        'bacd', 'badc', 'bcad', 'bcda', 'bdac', 'bdca',
        'cabd', 'cadb', 'cbad', 'cbda', 'cdab', 'cdba',
        'dabc', 'dacb', 'dbac', 'dbca', 'dcab', 'dcba']

assert list(''.join(x) for x in permutations('abcd',2)) == \
       ['ab', 'ac', 'ad',
        'ba', 'bc', 'bd',
        'ca', 'cb', 'cd',
        'da', 'db', 'dc']

# we can use these generators to create some simple but useful
#   other combinatorial generators

# the powerset yields all of the possible combinations of 
#   any number of elements from a given iterable
# this function will consume a generator
from itertools import combinations
def powerset( iterable ):
	iterable = list(iterable)
	for r in xrange(1,len(iterable)+1):
		for x in combinations( iterable, r ):
			yield x

assert [''.join(x) for x in powerset('abc')] == \
       ['a','b','c','ab','ac','bc','abc'] 

# all permutations is all of the possible permutations
#   of any number of elements from the given iterable
# this is different from the powerset in that the result is 
#   ordered
# this function will consume a generator
from itertools import permutations
def all_permutations( iterable ):
	iterable = list(iterable)
	for r in xrange(1,len(iterable)+1):
		for x in permutations( iterable, r ):
			yield x

assert [''.join(x) for x in all_permutations('abc')] == \
       [ 'a','b','c',
         'ab','ac','ba','bc','ca','cb',
         'abc','acb','bac','bca','cab','cba' ]

# here is a simple, brute-force solver for a word-finder game

# pick a random set of seven letters from the bag
from random import choice
from string import ascii_lowercase
letters = [choice(ascii_lowercase) for _ in xrange(7)]

# load words from a dictionary
dictionary_file = '/usr/share/dict/words'
try:
	with open( dictionary_file ) as f:
		dictionary = set( x.strip().lower() for x in f )
except IOError as e:
	from sys import stderr
	print >>stderr, 'cannot load dictionary file %s' % dictionary
	print >>stderr, 'using simple default dictionary'
	print >>stderr, e
	dictionary = {'a','apple','b','ball','c','cat','d','dog'}
# produce output
print 'given:', letters
# valid words are the set of all permutations union with the
#   set of all words in the dictionary
print 'valid words:', ', '.join( sorted(
   {''.join(x) for x in all_permutations(letters)} & dictionary ))

# one note about the above:
# coming from a language without common exceptions, one might be
#   tempted to use them very liberally in Python, wrapping
#   every piece of code in a try: ... except Exception: ... block
# the above demonstrates a good general principal: don't handle
#   exceptions unless you can actually do something about the
#   error; in this case, we substitute a hard-coded sample
#   dictionary for the dictionary read from file
# if we were not able to provide a good substitue for the dictionary
#   variable, we could have put the rest of the processing
#   code in the try-clause, to prevent the example from continuing
#   or we could have let the exception terminate the running of 
#   this programme by not catching it at all or we could have
#   translate the exception into a more informative exception
#   (which is made very elegant by Python 3.3<'s raise ... from ...
#   syntax)

# itertools.takewhile
# itertools.dropwhile

# takewhile, dropwhile take a predicate and an iterable
# like ifilter, they apply the predicate to every element of the
#   iterable, and either return every element UNTIL that predicate
#   becomes False (takewhile) or return every element AFTER that
#   predicate becomes True  

iseven = lambda x: x % 2 == 0
isodd  = lambda x: x % 2 != 0

from itertools import takewhile
assert list(takewhile(iseven,[2,4,6,8,9,11,14,16,20])) == [2, 4, 6, 8]

from itertools import dropwhile
assert list(dropwhile(isodd, [1,3,5,7,8,12,17,21,23])) == [8, 12, 17, 21, 23]

# DECORATORS

# decorators are generally useful in cases where you want to extract
#   some common functionality from a set of functions
#   where this functionality can be wrapped around the function

from sys import stderr
def foo( n ):
	print >>stderr, 'foo', n  # log invocation
	return 'foo' * n
def bar( n ):
	print >>stderr, 'bar', n
	return 'bar' * n

# the following two lines will log 
#   something to stderr
assert foo( 2 ) == 'foofoo'
assert bar( 2 ) == 'barbar'

# however, we can extract these common lines
#   into a decorator
# this may be a good idea, because we don't repeat
#   ourselves, and we also remove some mechanism
#   from the two functions that is not related to their
#   core purpose 
def logger( func ):
	def wrapper( n ):
		print >>stderr, func.__name__, n
		return func( n )
	return wrapper

@logger
def foo( n ):
	return 'foo' * n
@logger
def bar( n ):
	return 'bar' * n

# the following two lines will log 
#   something to stderr
assert foo( 2 ) == 'foofoo'
assert bar( 2 ) == 'barbar'

# property, classmethod, staticmethod
# __builtins__.property
# __builtins__.classmethod
# __builtins__.staticmethod

# property, staticmethod, and classmethod are probably
#   the three most common decorators you will use

# these decorators are used in class bodies to identify methods that are
#   property: properties of the class (i.e., mimic attribute syntax)
#   classmethod: methods in the scope of the class (not the instance)
#   staticmethod: methods not in the scope of the class or instance
#                 but merely in the namespace of the class

class Foo( object ):
	@property
	def x( self ):
		return 10
foo = Foo()
assert foo.x == 10 # a property looks like an attribute

class Foo( object ):
	@property
	def x( self ):
		return self._x
	@x.setter
	def x( self, x ):
		self._x = x
foo = Foo()
foo.x = 20
assert foo.x == 20 # you can use property to create attribute-like
                   #   getters, setters, and deleters

class Foo( object ):
	BAR = 10
	@classmethod
	def bar( cls ):
		return cls.BAR
foo1, foo2 = Foo(), Foo()
assert foo1.bar() == foo2.bar()
foo1.BAR = 100
assert foo1.bar() == foo2.bar() # even though we reassigned foo1.BAR
                                #   the .bar property is looking at
                                #   the value of BAR at the class level
                                #   so it doesn't know about changes
                                #   at the instance level  

class Foo( object ):
	@staticmethod
	def bar():
		return 'bar'
foo = Foo()
assert foo.bar() == 'bar'

# @functool.wraps

# when writing decorators, you may notice that 
#   you want the decorated (wrapped) function to have
#   the same docstring, name, &c. as the original function
from functools import wraps
def logger( func ):
	'''logger adds logging to a function'''
	@wraps( func )
	def wrapper( *args, **kwargs ):
		print 'calling %s' % func.__name__
		rv = func( *args, **kwargs )
		print 'returning %s' % rv
		return rv
	return wrapper

@logger
def double( x ):
	'''double(x) takes a number and returns its double'''
	return 2*x

assert double.__doc__ == 'double(x) takes a number and returns its double'

# @document

# the @-symbol is used in Java for annotations
# Python3 has its own annotation mechanism, but we could
#   use decorators as a form of documentation in a similar fashion
def document( *lines ):
	def decorator( func ):
		func.__doc__ = '\n'.join([func.__doc__ or '']+list(lines))
		return func
	return decorator
def precondition( *lines ):
	return document(*('precondition: ' + x for x in lines))
def postcondition( *lines ):
	return document(*('postcondition: ' + x for x in lines))

@postcondition( 'retval > 0' )
@precondition( 'x >= 0' )
@document( 'assumes IEEE-754 floating point arithmetic' )
def root( x ):
	return x ** 0.5
print root.__doc__

# @register

# you could also use decorators to perform global registration functions
# if you have 

# CONTEXT MANAGERS

# context managers are very well suited to the code pattern where
#   some code must be run before and after some business logic,
#   generally to modify and then unmodify some global state

# let's say we want to redirect stdout and stderr
# we want print statements to just append to some variable in memory
#   similar to use of stringstream in C++ 

# we might write this as follows
def foo():
	print 'foo'

import sys
from StringIO import StringIO
buf = StringIO()
old = sys.stdout, sys.stderr          # save
sys.stdout, sys.stderr = buf, buf     # set
try: 
	foo()                             # business logic
finally:
	sys.stdout, sys.stderr = old      # restore
	assert buf.getvalue() == 'foo\n'

# notice these problems:
#   1. the mechanism around redirecting stdout and stderr crowds out
#      our actual business logic
#   2. we have to repeat these blocks of code every time we want to
#      redirect stdout, stderr
#   3. it's very easy for us to forget to restore the previous
#      state of stdout, stderr
#   4. if some exception gets thrown in the business logic,
#      we're have to be sure our error handling will correctly restore
#      the previous tate 

# let's write a simple context manager to extract this functionality
# we'll write it using the contextmanager decorator
#   which allows us to write our context manager as a generator
#   that yields a single value
# code before the yield is the setup code
#   and code after the yield is the teardown code
from contextlib import contextmanager
import sys
@contextmanager
def capture_print( stdout, stderr ):
	# set up
	sys.stdout, sys.stderr, old = stdout, stderr, (sys.stdout, sys.stderr)
	# yield control to `with` block
	try: 
		yield 
	# clean up
	finally: 
		sys.stdout, sys.stderr = old

# rewriting the above
from StringIO import StringIO
buf = StringIO()
with capture_print( buf, buf ):
	foo() 
assert buf.getvalue() == 'foo\n'

# open in __builtins__ has been extended to act as a context manager
# this is probably the most frequency context manager you will use

# *this magic line*

# let's read from this very file without using context managers
filename = __file__
fh = open( filename )
assert any('# *this magic line*' in x.strip() for x in fh) 
fh.close()

# now, you may be able to write this in a single line as follows:
assert any('# *this magic line*' in x.strip() for x in open( filename ))

# this code will work and may not even show any erroneous behaviour
# it will work, because the __del__ member on a file object
#   closes and cleans up for you
# therefore, when the object created by open() falls out of its last
#   scope (i.e., its reference count falls to zero,) then the GC
#   will be free to call __del__
# however, the GC is not guaranteed to run after an object's reference
#   count goes to zero; in fact, one can disable the gc entirely 
#   by using gc.disable()
# additionally, the `del` keyword does not result in an object being
#   cleaned up or its __del__ method being called; all `del` will do is
#   decrement the reference count of the object by one.
# the actual garbage collection will be left to the garbage collector
# (this should make sense, because when we del a name in our current scope,
#  there is no way for us to know whether the object that name is bound to
#  is referenced in some other part of our programme)
# as a result, it's generally not a good idea to try to implement
#   C++ style RAII in Python; instead, we should use explicit contextmanagers

# with a context manager:
filename = __file__
with open( filename ) as f:
	assert any('# this magic line' in x.strip() for x in f) 

# context managers do not need to be used for just resource allocation
# we can use them for any code that requires some set up and tear down/clean up
# say we have a portfolio of stocks that we want to subject to
#   various combinations of basic market movements (sector-based scenarios)

from collections import namedtuple
Stock = namedtuple( 'Stock', 'ticker sector price volume' )

# this context manager represents a market movement:
#   it takes a set of stocks and yields a modified version of those
#   stocks based off of shifts provided in the form of functions
#   in a sector-keyed dictionary
class MarketScenario( object ):
	def __init__( self, stocks, shifts ):
		self.stocks, self.shifts = stocks, shifts
	def __enter__( self ):
		return ( Stock(ticker,
		               sector,
		               self.shifts.get(sector,lambda x:x)(price),
		               volume)
		         for ticker,sector,price,volume in self.stocks )
	def __exit__( self, type, value, traceback ):
		pass

portfolio = ( Stock('ADBE',  'infotech',     31.5,  870),
              Stock('AET',   'health',       42.4,  540),
              Stock('AGN',   'health',       90.8,  830),
              Stock('BRK.B', 'financials',   80.0,  630),
              Stock('BA',    'industrials',  68.4,  310),
              Stock('CPB',   'consumer',     31.6,  250),
              Stock('CAT',   'industrials',  86.2,  670),
              Stock('F',     'consumer',     10.5,  540),
              Stock('GOOG',  'infotech',    579.8,  350),
              Stock('XOM',   'energy',       79.3,  610) )

# post FB-IPO, IT companies take a hit
facebook_ipo = { 'infotech': lambda x: x*.75 }
# post Global Financial Crisis, banks are doing
#   great, consumer is doing terrible, but industrial
#   interests are still going strong
post_gfc = { 'financials' : lambda x: x*2,
             'consumer'   : lambda x: x*.25,
             'industrials': lambda x: x*1.1, }
# the natural gas revolution is a boon to the hydrocarbon
#   industry, and cheap power helps IT companies
#   invest in larger servers and data centres 
nat_gas = { 'energy'  : lambda x: x*1.2,
            'infotech': lambda x: x*1.2 }

# try with two market scenarios
with MarketScenario(portfolio, facebook_ipo) as p:
	with MarketScenario(p, nat_gas) as p:
		market_value = sum(x.price*x.volume for x in p)
		print market_value

# try with two different market scenarios
with MarketScenario(portfolio, facebook_ipo) as p:
	with MarketScenario(p, post_gfc) as p:
		market_value = sum(x.price*x.volume for x in p)
		print market_value

# when we have nested context managers, we can
#   use the following syntax (in Python 2.7<)
with MarketScenario(portfolio, facebook_ipo) as p, \
       MarketScenario(p, nat_gas) as p:
	market_value = sum(x.price*x.volume for x in p)
	print market_value

with MarketScenario(portfolio, facebook_ipo) as p, \
       MarketScenario(p, post_gfc) as p:
	market_value = sum(x.price*x.volume for x in p)
	print market_value

# another example of a useful context manager
#   is in decimal
# decimal provides us with a library for high precision
#   decimal arithmetic; if you work in finance 
#   and deal with actual sums of money, you probably 
#   should be using high precision decimal arithmetic
#   instead of lossy float arithmetic

# normally, 1/7 and 355/133 are roughly .1428 and 3.1415
from decimal import Decimal
assert 0.14285 < Decimal(1)   / 7   < 0.14286
assert 3.14159 < Decimal(355) / 113 < 3.14160

# they should differ by about .0013
assert (Decimal(355)/113) - (Decimal(1)/7) != 3.0

# decimal.localcontext, however, provides us with
#   a way to locally and temporarily set certain
#   parameters of our calculation context
# localcontext should be threadsafe

# let's try reducing precision to just two decimal places
from decimal import localcontext
with localcontext() as ctx:
	ctx.prec = 2
	assert 0.13 < Decimal(1)   / 7   < 0.15
	assert 3.0  < Decimal(355) / 113 < 3.2
	assert (Decimal(355)/113) - (Decimal(1)/7) == 3.0

# the changes to precision we made in localcontext
#   exist only within the `with` block
# once outside, we return to our previous state
assert 0.14285 < Decimal(1)   / 7   < 0.14286
assert 3.14159 < Decimal(355) / 113 < 3.14160
assert (Decimal(355)/113) - (Decimal(1)/7) != 3.0

# we may have a programme that needs to display information
#   for users in different locales
# locales are are managed globally so it would be very 
#   risky and tricky for us to write setup and teardown
#   code every time we want to display a localised message

# unfortuantely, none of the following is threadsafe

# let's write a context manager for it!
from locale import getlocale, setlocale, localeconv, LC_ALL
from contextlib import contextmanager
@contextmanager
def localecontext( *locale ):
	old = getlocale()             # save the old locale
	setlocale( LC_ALL, locale )   # set the new locale
	yield localeconv()            # yield the locale conventions
	setlocale( LC_ALL, old )      # restore the old locale

# now, whenever we want to display a localised
#   value, we do it within a localecontext()
#   block and can be sure that global state
#   is handled correctly and safely
from locale import currency
with localecontext( 'en_us', 'utf8' ):
	assert currency(1000, grouping=True) == '$1,000.00'
with localecontext( 'en_gb', 'utf8' ):
	assert currency(1000, grouping=True) == 'Â£1,000.00'

# locales present us with a situation where some API 
#   makes global modifications and we want to wrap them 
#   in a safe way

# sometimes, we also have an API that follows an open/close
#   mechanism for managing a resource or a connection

# contextlib provides us with a nice wrapper, closing(),
#   to automatically turn objects with a .close() method
#   into a context manager

from urllib2 import urlopen, HTTPError
from contextlib import closing
with closing(urlopen('http://www.python.org', timeout=1)) as page:
	# uncomment the below if you have internet access
	#assert any('python' in x.strip().lower() for x in page)
	pass

# we can write lots of context managers to track and control
#   state
# for example, say we have an SQLite database that we want
#   to do some quick calculations in

# we want to create a table, insert records,
#   select from the table, then drop the table

# we might write this as follows:
from sqlite3 import connect, OperationalError
conn = connect('example.db')
cursor = conn.cursor()
try:
	cursor.execute( 'DROP TABLE employees' )
except OperationalError:
	pass
cursor.execute( 'CREATE TABLE employees (name text, salary real)' )
cursor.execute( 'INSERT INTO employees VALUES ("janet", 200000)' )
cursor.execute( 'INSERT INTO employees VALUES ("john",  400000)' )
assert 600000.00 == \
       sum(r[0] for r in cursor.execute('SELECT SUM(salary) FROM employees'))
cursor.close()
conn.close()

# clearly, we can wrap connect() in contextlib.closing()
#   since it follows an open/close paradigm
# note that in Python 2.6<, connect() is already a context manager
#   that does commit/rollback transactions
from contextlib import contextmanager
@contextmanager
def connectioncontext( *args ):
	try:
		with connect( *args ) as conn:
			yield conn
	except:
		raise
	else:
		conn.close()

# we can also create a simple context manager for the
#   cursor to create it and close it 
from contextlib import contextmanager
@contextmanager
def cursorcontext( conn ):
	cursor = conn.cursor()
	try:
		yield cursor
	finally:
		cursor.close()

# rewriting with the two context managers:
from contextlib import closing
with connectioncontext('example.db') as conn:
	with cursorcontext( conn ) as cur:
		try:
			cur.execute( 'DROP TABLE employees' )
		except OperationalError:
			pass
		cur.execute( 'CREATE TABLE employees (name text, salary real)' )
		cur.execute( 'INSERT INTO employees VALUES ("janet", 200000)' )
		cur.execute( 'INSERT INTO employees VALUES ("john",  400000)' )
		assert 600000 == \
		  sum(r[0] for r in cur.execute('SELECT sum(salary) from employees'))
		cur.execute( 'DROP TABLE employees' )

# as before, we can nest these to reduce one level of indentation:
with connectioncontext('example.db') as conn, \
       cursorcontext( conn ) as cur:
	try:
		cur.execute( 'DROP TABLE employees' )
	except OperationalError:
		pass
	cur.execute( 'CREATE TABLE employees (name text, salary real)' )
	cur.execute( 'INSERT INTO employees VALUES ("janet", 200000)' )
	cur.execute( 'INSERT INTO employees VALUES ("john",  400000)' )
	assert 600000 == \
	  sum(r[0] for r in cur.execute('SELECT sum(salary) from employees'))
	cur.execute( 'DROP TABLE employees' )

# the creation and deletion of the table should
#   also suggest the use of a contextmanager

# let's create a context manager that adds a new
#   table and removes it when we're done

from contextlib import contextmanager
@contextmanager
def tablecontext( cursor, table, *fields ):
	try:
		# using string interpolation like this is probably
		#   a bit hacky
		cursor.execute( 'DROP TABLE %s' % table )
	except OperationalError:
		pass
	cursor.execute( 'CREATE TABLE %s (%s)' % (table, ', '.join(fields)) )
	yield table
	cursor.execute( 'DROP TABLE %s' % table )

# now, we can combine all of these into the following:
with connectioncontext('example.db') as conn, \
       cursorcontext( conn ) as cur, \
	     tablecontext(cur, 'employees', 'name text', 'salary real') as table:

	# business logic
	insert = 'INSERT INTO %s VALUES (?, ?)' % table
	employees = (('janet', 200000), ('john',  400000))
	cur.executemany( insert, employees )

	# check
	select = 'SELECT sum(salary) from employees'
	assert 600000 == sum(r[0] for r in cur.execute(select))

# this might be going a bit overboard, but note that if any step in our
#   set up or in our business logic fails, we will gracefully
#   rollback the state of our table, the state of our cursor, and the state
#   of our connection
# additionally, we have factored out code that we are likely to commonly
#   use
