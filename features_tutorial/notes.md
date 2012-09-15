# Python's cool features

- Speaker: V James Powell (vpowell@gmail.com)


## Decorators

- Most people say a decorator is a function that:
    - Takes a function
    - Returns a function
- However, you can technically return anything you want.  So, you can use a
  generator as a decorator.  This could be useful for doing something that you
  only want to do once but cannot hardcode for whatever reason.
    - Need a good example...

## Generators

- Just some object that has internal state that returns data every time you
    ask for it.
- Read-world example:
    - Computations that have very strict sequence.
    - Take an action that takes 3 steps, each step is done by a function.
    - The functions are always called in a specific order.
    - You could put them all in the top-level module scope, but this is lying
      to the user implying that these methods are dependent on each other and
      only useful when called in a specific order.
    - So code a generator to encapsulation each of these 'step' functions and
      yield the result for each one.

```python
def process():
    yield step1()
    yield step2()
    yield step3()
```

- Good way to keep track state without having to write the state logic tracking
  code yourself.

*itertools written in C, designed to use as little memory as possible*

```python

from itertools import tee, izip
def pairwise(iterable, n):
    iterables = tee(iterable, n)
    for i, it in enumerate(iterables):
        for _ in xrange(i):
            next(it)

    return izip(*iterables)
```

- tee: takes iterable and splits into 2 independently running iterables
    - Good to prevent exhausting a generator/iterable
    - You can exhaust it twice
    - Memory-efficient copy

```python
from itertools import count
def fizzbuzz():
    for x in count():
        if x % 3 == 0:
            yield 'fizz',

        elif x % 5 == 0:
            yield 'buzz',

        else:
            yield str(x)

n = 0
for num in fizzbuz():
    print num

    if n > 10:
        break

    n +=1
```

- Get random sampling of lines from ANY iterable:

```python
def randlines( iterable, n):
    for line in iterable:
        if randit(0, n) == 0:
            yield line
```

- Accumulate a specific amount of data before sendig a packet

```python
def router(iterable, packet_size):
    for datum in iterable:
        packet.append(datum)
        if len(packet) == packet_size:
            yield packet
            packet = []
```

- Python 3 fanciness

- `raise from` raise an exception in an exception block
- `yield from` is a new feature in Python 3
    - Delegate from subgenerators
    - Adds `for x` in code

- Only available in Python 3.3

- Flatten a list:

```python
flatten = (None for subgen in gen if (yield from subgen) and False)
```


## Context Mangers

- Reduce decimal precision to 2 places in a specific context

```python
from decimal import localcontext
with localcontext() as ctx:
    ctx.prec = 2
    assert 0.13 < Decimal(1)
    assert 3.0 < Decimal(355)
    assert (Decimal(255/113) - (Decimal(1)/7) == 3.0

```

- Use context manager to save bit flags for a specific portion of time
    - Good for hardware programming

- Locales

```python
from local import currency
with localcontext('en_us', 'utf8'):
    assert current(1000, groupt-True) -- '$1,000.00'
with localcontext('en_gb', 'utf8'):
	assert currency(1000, grouping=True) == 'Â£1,000.00'
```

- More example ideas:
    - Create temporary table in a database and have context manager clean it up
    - Monkey-patch something inside of a context and roll it back
    - Capture print statements in a specific piece of code and push somewhere
      else for the time being.



#### Difference between Context Manager and Decorator

- You can easily write decorator that does what a context manager does.
- Use a context manager if:
    - Don't want your code to be put into a function itself.
    - Using `with` keyword is more clear intent.
    - Need access to context inside the function your wrapping.


### Itertools

- takewhile(predicate, iterable) --> takewhile object
    - Return successive entries from an iterable as long as the 
      predicate evaluates to true for each entry.

- count(start=0, step=1) --> count object
    - Return a count object whose .next() method returns consecutive values.


* Oil industry has the best compression algorithm in the world.  Take huge
   amounts of data and reduce it to a single bit: Oil or no oil.*


##### Mind == Blown

- Look into Python C code to see what try/except does and write wild stuff:
- Drop this is in your code for a `switch` statement :)

```python
switch = lambda val: type('switch_meta', (type,), {})('switch',
                        (BaseException,), {'val': val})()
case = lambda pred: type('case_meta', (type,), {'__subclasscheck__': lambda
                    self, obj: pred(obj.val)})('case', (BaseException,),{})
default = case(lambda...
```

```
x = 11
try: raise switch(x)
except  case( lambda x: x % 2 == 0):
            print 'number is even'
except  default:
            print 'number is odd'
```


```
from dis import dis

def foo():
    pass

dis(foo)
```

- Look in Python source Python/ceval.c to see what byte code does in C code


#### Files
    - http://dl.dropbox.com/u/105629131/motivation.py
    - http://dl.dropbox.com/u/105629131/syntax.py
    - http://dl.dropbox.com/u/105629131/magic.py
