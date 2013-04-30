from sys import argv
import ply.lex as lex

# script, input_script = argvs
input_script = """
//: please ignore
this ://
\/ list listA = [1,2,3,4,5];
\/ int num1 = 20;
\/ int num2 = 10;

fun (int x, int y) -> funName -> int {
    call listThing itemin listA[-2]{
        y = 283 + -29 * listThing;
        return "some string here" + x;
    }
}

(num1, num2) --> funName;
"""

# input_script = "a = 10 + 2 b = a * 3 log(b) c = (b + 10) * 3"

# reserved words so the longest regex (ID) isn't used first and wrongly captured as an ID token
reserved = {
    'use' : 'USE',
    'fun' : 'FUN',
    'return' : 'RETURN',
    'call' : 'CALL',
    'itemin' : 'ITEMIN',
    'log' : 'LOG',
    'if' : 'IF',
    'else' : 'ELSE',
    'or' : 'OR',
    'orif' : 'ORIF',
    'and' : 'AND',
    'not' : 'NOT',
    'none' : 'TYNONE',
    'int' : 'TYINT',
    'string' : 'TYSTRING',
    'list' : 'TYLIST',
    'bool' : 'TYBOOL',
    'map' : 'TYMAP',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'elif' : 'ELIF',
    'startup' : 'STARTUP'
}

# declaring tokens
tokens = [
    'EMCSQ', 'SLCOMMENT', 'SEMICOLON', 'GLOBAL', 'STRING', 'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'LCBRACE', 'RCBRACE', 'DOT', 'COMMA', 'ARROWED', 'ASSIGN', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER', 'MODULO', 'LESS', 'GREATER', 'LESSEQ', 'GREATEQ', 'ISEQ', 'NOTEQ', 'ID','NUMBER',
    ] + list(reserved.values())

# token capturing
"""EASTER EGG SHENANIGANS...do I want to allow anything to be written within the brackets? If so, what happens with that?"""
t_EMCSQ     = r'EmC\[\]'
t_SLCOMMENT = r'//[^:][^\n]*'
t_SEMICOLON = r';'
t_GLOBAL    = r'\\/'
t_STRING      = r'("[^"]*")'  # |(\'[^']*\')' # must have line count

t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACK    = r'\['
t_RBRACK    = r'\]'
t_LCBRACE    = r'\{'
t_RCBRACE    = r'\}'

t_DOT       = r'\.'
t_COMMA     = r','
t_ARROWED   = r'->'   # or '->' ?

t_ISEQ    = r'=='
t_ASSIGN  = r'='
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_POWER   = r'\^'
t_MODULO  = r'%'

t_LESS      = r'<'
t_GREATER   = r'>'
t_LESSEQ    = r'<='
t_GREATEQ   = r'>='
t_NOTEQ     = r'!='

"""NOT USING NOW """
"in"
"not"
"<>"
"<<"
">>"
"~"
"lambda"

""" should carriage return \r really be ignored? """
# Ignored characters
t_ignore = ' \t\v\r' # ignres ALL whitespace (but not newlines, so those can be counted--just tabs, vertical tabs, and carriage returns)

states = (
    ('emcomment','exclusive'),
)

t_emcomment_ignore = ' \t\v\r'

# why couldn't you ignore single line comment with this: t_ignore = r'//:'
"""
or perhaps you could ignore it with a definition that comes before all other definitions (though i suppose newline could mess that up because you'd NEED to make sure it was running first to be considered the right line...wait then doesn't that mean that this IGNORE thing going on here will make multi-line comments fuck up the newline count?! oh wow, you can use token.value.count('\n) even though it's being 'ignored'):

def t_ONELCOMMENT(token):
    r'//'
    pass
"""

def t_begin_emcomment(token):
    r'//:'
    token.lexer.begin('emcomment')

def t_emcomment_end(token):
    r'://'
    # makes sure to count lines
    "but why is this in END and not in the start of the state?"
    token.lexer.lineno += token.value.count('\n')
    # goes back to non-comment mode
    token.lexer.begin('INITIAL')

def t_emcomment_error(token):
    # skips over EVERYTHING you find until you get to the end of the comment
    # this is similar to pass, but gathers up all the symbols so that you can count the newlines later at the t_emcomment_end part
    token.lexer.skip(1)

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
        # += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'ID')
    return t

def t_NUMBER(t):
    r'-?((\d+(\.\d+)?)|(\.\d+))' # should include neg/pos either '[nums]' or '[numss].[nums]' or '.[nums]''
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    # return float(t)
    return t


class TokenObj(object):
    def __init__(self, type, value, pos):
        self.type = type
        self.value = value
        self.pos = pos
    def __repr__(self):
        return "Name: %s; Value: %s; Position: %s" % (self.type, self.value, self.pos)



# Build the lexer
emcsqlexer = lex.lex()

# def tokenize():
emcsqlexer.input(input_script)


# Tokenizer
string_form = ''
output = []
list_tuples_form = []
pratt_obj_form = []
constants_list = []
while True:
    tok = emcsqlexer.token()
    
    if not tok: break
    
    output.append(tok)
    list_tuples_form += [(tok.type, tok.value)]
    string_form += "%s %s" % (tok.type, tok.value)
    token = TokenObj(tok.value, tok.type, tok.lexpos)
    pratt_obj_form.append(token)
    if tok.type == 'STRING' or tok.type == 'NUMBER':
        constants_list += (tok.type, tok.value)
    # print tok.type, tok.value, tok.lexpos
# prints it in a way pratt parser could use
# print string_form
print list_tuples_form
print constants_list
print pratt_obj_form


# def em_lexer(lexer,input_script):
#   pass
  