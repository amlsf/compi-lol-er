'''
 * The primary entry point is PyAST_Compile(), which returns a
 * PyCodeObject.  The compiler makes several passes to build the code
 * object:
 *   1. Checks for future statements.  See future.c
 *   2. Builds a symbol table.  See symtable.c.
 *   3. Generate code for basic blocks.  See compiler_mod() in this file.
 *   4. Assemble the basic blocks into final code.  See assemble() in
 *      this file.
 *   5. Optimize the byte code (peephole optimizations).  See peephole.c
 *
 * Note that compiler_mod() suggests module, but the module ast type
 * (mod_ty) has cases for expressions and interactive statements.
 *
 * CAUTION: The VISIT_* macros abort the current function when they
 * encounter a problem. So don't invoke them when there is memory
 * which needs to be released. Code blocks are OK, as the compiler
 * structure takes care of releasing those.  Use the arena to manage
 * objects.
 '''

from peak.util.assembler import Code
from dis import dis

# from emcsq_pratt_parser import AST
# from emcsq_ply_lexer import constants_list
# from emcsq_pratt_parser import symbol_table

# int x = 5;
# int y = 10;
# int z = x + y;

'''WHAT SHOULD I KEEP TRACK OF'''
const_tacker = 0
var_tracker = 0
# symbol_table -- down below

const_table = {
	
}

c = Code()

# AST for:
# int x = 5;
ast = ('stmt', 
		('decl', 
			(('type', 'int'),
				('id', 'x')),
			(('expr', 
				('literal', 5)))))

	# decl --> loa
def emit(emission):
	dis(emission.code())

def generate(input):
	print input
	necFun = symbol_table[input[0]]
	necFun(input[1])

def gen_block(input):
	pass

def gen_stmt(input):
	# input = ('decl',(('type', 'int'),('id', 'x')), ('expr', ('literal', 5)))
	# whatever it is, call the method for the appropriate function
	# if the first slot is 'decl' or like anything that requires a different unknown method
	necFun = symbol_table[input[0]]
	# you know that if it's a decl, there will only every be 1 way that's going to go
	if input[0] == 'decl':
		necFun(input[1], input[2])

def gen_decl(identifier, expr):
	# input = ('decl',(('type', 'int'),('id', 'x')), ('expr', ('literal', 5))))
	# ignore type for python VM compiler!!
	print identifier, expr
	# add to symbol table if not in there
	# try 
	# throw error if already in symbol table
	# except
	# symbol_table.get((input[1], input[2])) # what was this method
	gen_expr(expr)
	gen_id(identifier[1])


	# is it this or c.emit(expr)
	return

def gen_expr(input):
	# input = ('exp', ('literal', 5))
	print input
	if input[1][0] == 'literal':
		c.LOAD_CONST(input[1][1])
		# load const?

def gen_id(identifier):
	print identifier[1]
	variable = "'"+identifier[1]+"'"
	print variable
	# c = Code()
	c.STORE_FAST(variable)
	c.LOAD_FAST(variable)

def gen_list(input):


symbol_table = {
	'block': gen_block,
	'stmt': gen_stmt,
	'decl': gen_decl,
	'expr': gen_expr,
}

generate(ast)
c.STOP_CODE
emit(c)
# dis(c.code())