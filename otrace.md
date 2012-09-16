# Introduction to OTrace

## OTrace

- Object tracing on live application
- Pure Python (some OS specific calls)
- Mapping all objects in running program to virtual file system
- Snapshots of traced variables also mapped to filesystem
    - snapshots can be pickled and achived in sqlite, etc.
- Object shell (oshell) to navigate and modify virtual file system
- Monkey patching to insert diagnostic code into a running program
    - Run vi live running code

- Object tagging for tracking objects across different methods

### Uses

- Tracing tool for debugging
- Console/dashboard for monitoring production servers
- Teaching tool for exploring innards of program
- Code patching tool for unit tests

### Internals

- Functions are decorated dynamically
- Runs in it's own thread
- Good for debugging something with an event loop

### oshell

- Prompt to browse your objects
- Can use `ls`, etc. to see classes and methods while application runs

### Monkey Patching

- Use `edit` command in `oshell`
- Opens your editor and allows you to modify the code in memory

### How

- See exception
- Trace function that is throwing exception
- Get exception to happen again
- otrace now will create a snapshot when sees exception
- Checkout out snapshot in `oshell` for variable contents, etc.
- Use `view -i <function>` to look at code of function throwing exception
- `set safe_mode False` on `oshell` command to allow monkey patching
- Monkey patch code live with `edit` open `vi` and change the function code
- Use `unpatch <function>` to remove your monkey patch
    - Also works if you quit program b/c it was patched in memory

#### Extras

- GraphTerm: Browser based GUI for otrace
- cgitb
