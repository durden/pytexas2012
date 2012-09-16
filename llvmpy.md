# LLVMPY

- Python interface to LLVM
- Use as a nice way to interface with LLVM
- Target your code to LLVM then LLVM can support multiple architectures
- [llvmpy](http://llvmpy.org)

## LLVM

    - Low Level Virtual Machine
    - Compiler infrastructure written in C++
    - Uses LLVM IR (Intermediate Representation)
    - Library (unlike GCC)

## LLVMPY

    - No need to write C++ code to generate LLVM
    - Easy to experiment with
    - Learning curve of LLM is steep
    - Supports LLVM 3.1

### Writing a Compiler

    - Lexical analysis produces tokens
    - Parser produces AST from tokens
    - Generate intermediate form from AST
    - Optimziation passes
    - Output (native) backend code

### Pascal to Python

    - Pascal compiler written in Python
      [pascal-in-python](http://github.com/alcides/pascal-in-python)
    - Uses PLY (Python Lex and Yacc)

### Numba

    - Python bytecode used as source and translated to LLVM (with LLVMPY)
    - Resulting C-level function pointer can be inserted into numpy run-time
    - Understands numpy arrays

### Bitey (Bitcode import tool)

    - Uses import hooks
    - Uses ctypes
    - Uses LLVMPY to inspect the bitcode for the function signatures
