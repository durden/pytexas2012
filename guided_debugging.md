# Guided debugging strategies

## Tools

- `print`
- `pdb`
    - `pdb.post_mortem()`
    - `pdb.set_trace()`
- `logging`
- `cProfile`
- unit/functional tests

## Causes of bugs

- Misunderstanding API/requirements
- Code is out of sync (function and caller don't agree)
- Environment assumptions are incorrect

## Bugs under load

- Reconsider assumptions about deallocation
- Failure to collect memory garbage
- Excessive nesting of stack frames
- Delayed temporary file deletion
- Exhaustion of threads or locks
- Changes in IO behavior (network)

**Wrtie a realistic unit test after fixing**

## Bugs that force running forever

- Setup a signal handler to Ctrl-C to jump into app to see where it is
- Setup an alarm signal to alert when code doesn't finish in what you think is
  a reasonable amount of time.

```python
import signal
def interrupt_handler(signum, frame):
    import pdb
    pdb.set_trace()

    # (on OSX, us signal.SIGNINT instead of SIGUSR1)
    signal.signal(signal.SIGUSR2, interrupot_handler)

signal.signal(signal.SIGALRM, interrupt_handler)
signal.alarm(30)
do_somehting
signal.alarm(0)
```
