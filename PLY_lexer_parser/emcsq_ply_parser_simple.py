import ply.yacc as yacc
import emcsq_ply_lexer
from emcsq_ply_lexer import tokens, output, string_form, pratt_form
# tokens = emcsqlexer.tokens

print "PARSER STARTING"

# binary ops
precedence = (
	# lowest priority vv
	('right', 'ASSIGN'),
	('left', 'PLUS'),
	('left', 'TIMES', 'DIVIDE'),
	# highest priority ^^
)

def p_error(err):
	print('error: %s' %err)

def p_program(p):
	'''program : stmts'''

def p_function_def(p):
	'''function_def : FUN ARROWED LPAREN params RPAREN ID ARROWED block
	| FUN ARROWED LPAREN RPAREN ID ARROWED block'''

def p_function_call(p):
	''' function_call : LPAREN params RPAREN ARROWED ID method
	| LPAREN params RPAREN ARROWED ID
	| LPAREN RPAREN ARROWED ID method
	| LPAREN RPAREN ARROWED ID
	'''

def p_block(p):
	'''block : LCBRACE stmts RCBRACE'''


def p_stmts(p):
	'''stmts : stmt SEMICOLON stmts
	| stmt SEMICOLON'''

def p_stmt(p):
	'''stmt : function_def
	| function_call
	| conditional
	| loop
	| GLOBAL ID ASSIGN expr
	| ID ASSIGN expr
	| RETURN expr
	| expr stmt
	| USE ID method
	| USE ID 
	| LOG LPAREN expr RPAREN'''

def p_conditional(p):
	''' conditional : IF expr block
	| IF expr block ELSE block
	| IF expr block optelif
	| IF expr block optelif ELSE block'''

def p_loop(p):
	''' loop : CALL ID ITEMIN ID range filter
	| CALL ID ITEMIN ID filter
	| CALL ID ITEMIN ID range
	| CALL ID ITEMIN ID '''

def p_optelif(p):
	''' optelif : ELIF expr block ELIF expr block
	| ELIF block '''

def p_params(p):
	'''params : type ID params
	| type ID'''

def p_range(p):
	'''range : LBRACK NUMBER COMMA NUMBER RBRACK'''

def p_filter(p):
	'''filter : LBRACK NUMBER RBRACK'''

def p_method(p):
	'''method : DOT ID method
	| DOT ID'''

def p_expr(p):
	'''expr : LPAREN expr RPAREN
	| expr PLUS expr
	| expr MINUS expr
	| expr TIMES expr
	| expr DIVIDE expr
	| expr MODULO expr
	| expr POWER expr
	| expr LESS expr
	| expr GREATER expr
	| expr LESSEQ expr
	| expr GREATEQ expr
	| expr ISEQ expr
	| expr AND expr
	| expr OR expr
	| expr NOT expr
	| expr NOTEQ expr
	| FALSE
	| TRUE
	| ID
	| NUMBER
	| STRING
	| type'''


def p_type(p):
	'''type : TYNONE
	| TYINT
	| TYSTRING
	| TYLIST
	| TYBOOL
	| TYMAP'''





yacc.yacc()

while 1:
	yacc.parse(string_form)
