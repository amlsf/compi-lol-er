Compi-lol-er
============

Writing a compiler for my made up language (EmC[], E=mc^2, Em's Compiler, emcetera emcetera) 
and experimenting with different methods to do so.

File Tree (In Progress):
----------------------
  - PLY_Lexer_Parser: This is one version of the lexer and parser that were fairly simple and not at all robust. As a result, I dropped this approach in order to use Pratt's methods which were far more creative and intriguing.
  - Pratt: THE OFFICIAL LEXER AND PARSER that are used with my compiler. His methods are explained fairly 
  - Udacity_Prog_Lang: Took the "Programming Languages" course (#262) on udacity.com, these python exercises were the most difficult and interesting to me both code-wise and theoretically
  - lisp_interpreter: Went through and coded Norvig's Lispy interpreter from http://norvig.com/lispy.html and because it was fairly straightforward, most of my personal involvement was in commenting to make sure that I fully understood all that was taking place
  - screenshots: ...screenshots...

Overview
-------------
My compiler came to be after a culmination of seemingly endless nights, scouring books and articles for something that would excite me and teach me more than all the rest (a difficult feat). Writing a compiler to Python VM brought me to work hard to discover what actually goes on behind the code we write, and really grapple with the logic a computer uses to run a program.

I wrote a compiler that takes an experimental language I created called EmC and compiles it to Python VM ByteCode(scoped for the 4 weeks with which I had to work on it) and is an ongoing project that will eventually compile to assembly. The language was not designed for usability, but rather as a more complicated syntax that would further challenge me and increase my learning due to inability to use the easy, Python-resembling ways out during parsing and code generation.

In summary, [emcc](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L2146) takes a file(the script), saves a variable of the script name, lexes the file into a list of Token objects, parses these tokens into an Abstract Syntax Tree using Pratt-style parsing, interprets the script (primarily to check validity of the script and AST), generates Python VM ByteCode (kept in a code object), disassembles and evaluates that to check that it is valid, and then writes that ByteCode to a pyc file.


BNF & FizzBuzz language example
--------------------------------------------------
Here resides the [Backus-Naur Form grammar](https://github.com/emi1337/compi-lol-er/blob/master/grammar_bnf.txt) that outlines the structure and rules of my language.
The most noticeable differences in my language from python involve the C-style blocks and line endings, loops, and function definition and invocation, which show the flow of where information(arguments) are going:
    
stmt --> FUN LPAREN optparams RPAREN ARROWED ID ARROWED type block
        
ex.) [Line1](https://github.com/emi1337/compi-lol-er/blob/master/fizzbuzz.emc#L1)
    
stmt --> SEND LPAREN optargs RPAREN ARROWED ID
    
ex.) [Line11](https://github.com/emi1337/compi-lol-er/blob/master/fizzbuzz.emc#L11)

Lexing
---------
I used PLY (Python Lex-Yacc), a tool that one normally uses to lex and parse a language. However, I wrote my own parser and tokenizing process. I simply [used PLY](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L38) to visually lay out my tokens in a clear manner and keep track of line/character positions.

All of this is launched from [a method](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L1919) that creates your lexer using the lex() function and then generates the tokens by feeding it an input script.

All the token names found in the 'tokens' list tell PLY to make a token out of every function that starts with 't_' and ends with a name in that list. It uses these methods by capturing text (the longest string of characters it can find from each token match) based on the [regular expression defined in the first line](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L1501) of each function and returns a list of all these tokens made up of the name, value, position in the line, and position in the full script. I used these methods to, instead of letting PLY create the tokens automatically their way, [create token objects](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L965) that had additional attributes that I would use in later stages: the precedance value (lbp), nulld methods and leftd methods that would be called during parsing, the eval methods that would be called during interpreting, and the emit methods that would be called during code generation.

The newline and emcomment methods have special uses in that the former increases the lexers current line count so that each token has the appropriate position attached, and all comments (single and multi-line) in my language are ignored by the lexer.

Pratt Parsing
------------------
I wrote a Pratt-style parser which uses an implementation of Pratt's algorithm, including [Douglas Crockford's extensions for parsing statements] (http://javascript.crockford.com/tdop/tdop.html) in order to extend my parser's functionality to include non-expressions. As a result, this technique is the same as recursive descent for most things, but uses the concept of 'token binding power' when dealing with expressions(precedence comparable to math's order of operations). Each token is given a number that describes how tightly it binds to the other tokens around it, eliminating the need for tricky operator precedence rules. The binding power attributes are specific to each token, not only in precedence, but also based on context: as a prefix (ex. the - sign to imply negative numbers) or infix(ex. -, +, *, /) operator. The other primary difference from most parsing techniques is the use of the lexed tokens as nodes in the resultant parse tree.

The standard recursive descent parser is kicked off in the [Program.stmtd method](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L1967). Each token that begins a statement form has a .stmtd (for 'statement denotation') method that recursively parses the remainder of the tokens into a valid statement, holding onto relevant information (in the token's attributes) as it parses.

The parser assumes each program is composed of statements, first attempting to execute a token's .stmtd method if it has one, otherwise parsing the token stream as an expression, which is where [Pratt's technique is used](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L2041). For every token, Pratt's technique considers both the previous token and the following one, and comparing the left token's binding power (the object attribute called 'lbp' , the higher of which represents a higher precedence in terms of order of operations) to the one on the right. 

Expression example: 1(null) +(lbp=110) 5(null) *(lbp=120) 3(null) -(lbp=110). 

The function keeps track of the partially evaluated expression to the left of the current token until the following token has a lower lbp (or the statement reaches the end). Once the next token has a lower lbp (meaning the previous part of the equation had a higher precedence and should be evaluated before whatever follows), the left side is returned.

Interpretation
------------------
The compiler includes a naive interpreter that was used to validate execution during development of the code generation phase. Interpretation is [straight-forward](#L484) recursive evaluation of the abstract syntax tree, starting the same way as parsing and code generation, from the Program node.

During evaluation, I use only a single environment dictionary to store variables. This means that the interpreter does not observe any lexical scoping rules during evaluation. All variables are global across all functions and persist beyond their lexical blocks. As interpretation was just used to validate progress, I wasn't too concerned with this limitation.

Code Generation
------------------------
Code generation was much trickier, particularly given that there is little to no documentation on how to target the Python VM. In fact, the Python core team describes the VM as a "moving target" that can have significant changes between minor versions, so getting code generation to work was a combination of guesswork, reading the original C source, and reverse engineering using Python's built-in disassembler module.

In general, Python executes all scripts on a stack-based VM whose opcodes can be found [here](http://docs.python.org/2/library/dis.html). The opcodes aren't too different from what I've seen a typical instruction set to be, except for the absence of any mention of registers. Instead, Python is stack-based, passing arguments and return values on a single, globally available stack. As an example, to add two numbers, you push the two operands on the stack, then execute the BINARY_ADD opcode, which pops both operands off and pushes the resultant value onto the stack in their place. The same is generally true for function calls as well, with special handling of keyword arguments.

For me, the biggest conceptual roadblock in targeting the Python VM was understanding that the bytecode representation of a program is not a single sequence where function definitions live at different memory addresses and program execution jumps back and forth between them. Instead, when compiled to bytecode, a python program is a group of 'code objects' that each contain the bytecode for a single function. Each of these code objects has a memory address space starting at 0 where the bytecodes are stored for execution. The entire program itself is then packed into a single top-level code object that needs to be loaded onto the stack prior to calling said function.

Basically, function invocation does not happen by jumping the program counter to the memory address of the beginning of the function. Instead, the program counter [jumps _inside_](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L1347) the [code object for the function](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L906), starting execution at the 0th address of that code object.

Once that was understood, code generation became more straightforward, recursively traversing the AST and emitting the corresponding bytecode into a code object that represented the enclosing function. I used a helper library, the PEAK bytecode assembler [here](peak.telecommunity.com/DevCenter/BytecodeAssembler) to construct the code objects, as it helpfully handled the calculation of absolute and relative jump targets when branching and looping. This is something I'll have to change when compiling to assembly.


Writing to a file
---------------------
To create a .pyc file, I used the marshal library python provides. I start [here](https://github.com/emi1337/compi-lol-er/blob/master/emcc#L2137) by creating a file using the name of the original script and adding on the .pyc suffix.  The .pyc file format demands a timestamp and a 'secret key'. I write out the first 4 bytes of the file as the timestamp and the next 4 as the key. The timestamp is used to compare when the file was last compiled and the secret key is python-version specific, so pyc files are not capable of being run on different versions of python. After the timestamp and the secret key, I dump the top-level code object into the file, first running it through the marshalling library, then close it.

The exact format of the .pyc is version specific. Aside from the timestamp and the secret key, the format of the marshalled code object is completely undocumented. As a result, we have to trust that if the code object is assembled correctly, and test accordingly (and consistently over time).

FinalThoughts
--------------------------------
I used the marshalling library and bytecode assembler as a result of the the in-memory structure and behavior of Python objects being completely undocumented. Therefore, my compiler is limited--because we cannot construct code objects in memory using the proper serialization, nor can we write the bytecodes to a file without the help of marshalling, my compiler can only target the Python VM if it is written in Python to begin with. As it stands, my compiler cannot be written in any other language. However, during the process of compiling to x86, this will no longer be an issue. 

Though my compiler successfully compiles functions and various loops, I am in the process of adding class and map funtionality. As I've mentioned before, I'll be working with registers and more complex line number consideration in my next stage of compilation.




![em-ster egg screenshot](https://raw.github.com/emi1337/compi-lol-er/master/screenshots/compiler_easteregg.jpg)
