# Recipes for debugging

## Sys module

- sys.displayhook, sys.__displayhook__
- sys.excepthook, __excepthook__

### Altering sys.path

1. Make sure to use append()
    - This won't work b/c it copies and reassigning a local (shadow)

```python
from sys import path
path = ['/test'] +path
```

## code.InteractiveConsole

- Nice trick to debug instead of using `pdb`
- No need to learn `pdb` syntax

```python
from rlcompleter import readline
readline.parse_and_bind('tab:complete')

from code import InteractiveConsole
IteractiveConsole(locals=locals().copy().interact('')
```

**readline and tablcompletion are not necessary, just helpful**

## Import Hooks

- Add import hook to graph everything that is imported

### Ideas

- Replace os.environ dict that a dict that logs when a key is accessed
    - Good to see what environment variables are actually used by the
      application and which are old/removable.
    - Use a context manager to track when you change the os.environ dict so
      that you always replace it with what you actually replaced at the start.
