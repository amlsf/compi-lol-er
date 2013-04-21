import ply.lex as lex

tokens = (
    'EMCSQ', 'SLCOMMENT', 'COMMENTST', 'STRING', 'SEMICOLON', 'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'LCBRACE', 'RCBRACE', 'ARROWED', 'COMMA', 'DOT', 'ASSIGN', 'OP','ID','NUMBER',
    )

# Tokens
"""EASTER EGG SHENANIGANS...do I want to allow anything to be written within the brackets? If so, what happens with that?"""
t_EMCSQ     = r'EmC\[\]'
"""FIGURE OUT HOW TO DEAL WITH COMMENTS/LINECOUNT NOT IN THIS HACKY WAY"""
t_SLCOMMENT = r'//'
t_COMMENTST = r'//:[^://]*://'
t_STRING    = r'("[^"]*")}(\'[^\']*\')'
t_SEMICOLON = r';'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACK    = r'\['
t_RBRACK    = r'\]'
t_LCBRACE   = r'{'
t_RCBRACE   = r'}'
t_ARROWED   = r'-->'
t_COMMA     = r','
t_DOT       = r'\.'
t_ASSIGN    = r'=' # should this be kept out of the other ops?
t_OP        = r'\+|-|\*|/|\^|%|<|>|>=|<=|==|!='
t_ID        = r'[a-zA-Z_][a-zA-Z0-9_]*'


""" THE OVERLY SPECIFIED TOKENS """
# t_COMMENTST = r'//:'
# t_COMMENTND = r'://'
# t_string      = r'("[^"]*")}(\'[^']*\')'
# t_SEMICOLON = r';'


# t_LPAREN  = r'\('
# t_RPAREN  = r'\)'
# t_LBRACK    = r'\['
# t_RBRACK    = r'\]'
# t_LCBRACE    = r'\{'
# t_RCBRACE    = r'\}'
# t_DOT       = r'\.'
# t_COMMA     = r','

# t_FUN     = r'fun' # function
# t_TAKES   = r'takes' # do I want this?
# t_ARROWED   = r'-->'   # or '->' ?
""" I MAY WANT TO REDO RETURN""" 
# t_RETURN  = r'return' # <-- ?? for symmetry?
""" I MAY WANT TO REDO USE""" 
# t_USE     = r'use'

# t_CALL    = r'call' # for loop 'for'
# t_ITEMIN  = r'itemin' # for loop 'in'
# t_LOG     = r'log' # print


# t_IF      = r'if' 
# t_ELSE    = r'else'
# t_OR      = r'or' # 
# t_ORIF    = r'orif'
# t_AND     = r'and'
# t_NOT     = r'not'

# t_NONE    = r'none'
# t_INT     = r'int'
# t_STRING  = r'string'
# t_LIST    = r'list'
# t_BOOL    = r'bool'

# t_PLUS    = r'\+'
# t_MINUS   = r'-'
# t_TIMES   = r'\*'
# t_DIVIDE  = r'/'
# t_ASSIGN  = r'='
# t_NUMBER    = r'-?((\d+[\.\d+]?)|(\.\d+))' # should include neg/pos either '[nums]' or '[nums].[nums]' or '.[nums]''

"""NOT USING NOW """
"in"
"not"
"is"
"<>"
"<<"
">>"
"~"
"lambda"

# fitted with nud method that returns symbol itself, uses lambda

# Ignored characters

t_ignore = ' \t\v\r' # ALL whitespace 

# why couldn't you ignore single line comments with this: t_ignore = r'/////:'
"""
or perhaps you could ignore it with a definition that comes before all other definitions (though i suppose newline could mess that up because you'd NEED to make sure it was running first to be considered the right line...wait then doesn't that mean that this IGNORE thing going on here will make multi-line comments fuck up the newline count?! oh wow, you can use token.value.count('\n) even though it's being 'ignored'):

def t_ONELCOMMENT(token):
    r'////'
    pass
"""

def t_emcomment(token):
    r'////:'
    token.lexer.begin('emcomment')

def t_emcomment_end(token):
    r':////'
    # makes sure to count lines
    "but why is this in END and not in the start of the state?"
    token.lexer.lineno += token.value.count('\n')
    # goes back to non-comment mode
    token.lexer.begin('INITIAL')

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
        # += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_NUMBER(t):
    r'-?((\d+[\.\d+]?)|(\.\d+))' # should include neg/pos either '[nums]' or '[nums].[nums]' or '.[nums]''
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return float(t)
    return t

    
# Build the lexer
emcsqlexer = lex.lex()

input_script = """
list listA = [1,2,3,4,5]
fun funName takes (arg1, arg2) --> int {
call x itemin listA[-2]{
y = 3.5 + 4 * 10;
EmC[];
return "some string here";
}
}
"""

emcsqlexer.input(input_script)

# Tokenizer
pratt_form = []
while True:
    tok = lexer.token()
    if not tok: break
    print tok
    pratt_form += [(tok.type, tok.value)]
    # print tok.type, tok.value, tok.line, tok.lexpos
# prints it in a way pratt parser could use
print pratt_form





# Parsing rules

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    )

# dictionary of names
names = { }

def p_statement_assign(t):
    'statement : NAME EQUALS expression'
    names[t[1]] = t[3]

def p_statement_expr(t):
    'statement : expression'
    print(t[1])

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    if t[2] == '+'  : t[0] = t[1] + t[3]
    elif t[2] == '-': t[0] = t[1] - t[3]
    elif t[2] == '*': t[0] = t[1] * t[3]
    elif t[2] == '/': t[0] = t[1] / t[3]

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    try:
        t[0] = names[t[1]]
    except LookupError:
        print("Undefined name '%s'" % t[1])
        t[0] = 0

def p_error(t):
    print("Syntax error at '%s'" % t.value)



# import ply.yacc as yacc
# yacc.yacc()

# while 1:
#     try:
#         s = input('calc > ')   # Use raw_input on Python 2
#     except EOFError:
#         break
#     yacc.parse(s)