from sys import argv
import ply.lex as lex

output = []
pratt_obj_form = []
constants_list = []
list_tuples_form = []

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


# token classes for pratt parser objectification
class Tok_Template(object):
    def __init__(self, type, value, pos):
        self.type = type
        self.value = value
        self.pos = pos
    def nud(self):
        raise SyntaxError(
            "Syntax error (%r)." % self.id
        )

    def led(self, left):
        raise SyntaxError(
            "Syntax error (%r)." % self.id
        )

    def __repr__(self):
        return "(Type: %s; Value: '%s'; Position: %s)" % (self.type, self.value, self.pos)
        # if self.id == "(name)" or self.id == "(literal)":
        #     return "(%s %s)" % (self.id[1:-1], self.value)
        # out = [self.id, self.first, self.second, self.third]
        # out = map(str, filter(None, out))
        # return "(" + " ".join(out) + ")" # you know everything will be displayed in parentheses


# symbol("if", 20) 
# ternary form
class Tok_If(Tok_Template):
    lbp = 20
    def nud(self):
        self.first = expression(lbp)
        self.second = None
        return self
    '''wait'''
    # symbol(id).nud = nud
    def led(self, left):
        self.first = left
        self.second = expression()
        '''need advance that doesn't break --> try? expect?'''
        advance("elif")
        advance("else")
        self.third = expression()
        return self

# symbol("if", 20) 
# ternary form
class Tok_Elif(Tok_Template):
    lbp = 20
    def nud(self):
        self.first = expression(lbp)
        self.second = None
        return self
    '''wait'''
    # symbol(id).nud = nud


# symbol("if", 20) 
# ternary form
class Tok_Else(Tok_Template):
    lbp = 20
    def nud(self):
        self.first = expression(lbp)
        self.second = None
        return self
    '''wait'''
    # symbol(id).nud = nud


# infix_r("or", 30)
class Tok_Or(Tok_Template):
    lbp = 30

class Tok_Orif(Tok_Template):
    lbp = 30

# infix_r("and", 40)
class Tok_And(Tok_Template):
    lbp = 40

# infix_r("not", 50)
class Tok_Not(Tok_Template):
    lbp = 50
    def led(self, left):
        if token.id != "in":
            raise SyntaxError("Invalid syntax")
        advance()
        self.id = "not in"
        self.first = left
        self.second = expression(60)
        return self

# infix("in", 60)
class Tok_In(Tok_Template):
    lbp = 60

# infix("not", 60) # in, not in
class Tok_Not(Tok_Template):
    lbp = 60

# infix("is", 60) # is, is not
class Tok_Is(Tok_Template):
    lbp = 60

# infix("<", 60);
class Tok_Less_Than(Tok_Template):
    lbp = 60

# infix("<=", 60)
class Tok_Less_Or_Eq(Tok_Template):
    lbp = 60

# infix(">", 60) 
class Tok_Greater_Than(Tok_Template):
    lbp = 60

# infix(">=", 60)
class Tok_Greater_Or_Eq(Tok_Template):
    lbp = 60

# infix("!=", 60); 
class Tok_Not_Eq(Tok_Template):
    lbp = 60

# infix("==", 60)
class Tok_Is_Equal(Tok_Template):
    lbp = 60

'''what is the diff between this and other or (the former being python's 'or' and the latter at lbp=60 being python's '|')'''
# # infix("|", 60)
# class Tok_PipeOr(Tok_Template):
#     lbp = 60

# # infix("&", 90)
# class Tok_AmpersAnd(Tok_Template):
#     lbp = 90

# infix("+", 110) 
class Tok_Plus(Tok_Template):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self
    "WHAT DO I DO WITH THIS"
    # symbol(id, bp).led = led

# infix("-", 110)
class Tok_Minus(Tok_Template):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self

# infix("*", 120) 
class Tok_Times(Tok_Template):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self

# infix("/", 120)
class Tok_Div(Tok_Template):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 

# infix("%", 120)
class Tok_Modulo(Tok_Template):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self     

# prefix("-", 130) 
class Tok_Negative(Tok_Template):
    lbp = 90

# infix_r("^", 140)
class Tok_Power(Tok_Template):
    lbp = 130
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 


# symbol("->", 140)
class Tok_Arrow(Tok_Template):
    lbp = 150

""" HOW DOES DOT NOTATION WORK """
# symbol(".", 150)
class Tok_Dot(Tok_Template):
    lbp = 150
    def led(self, left):
        if token.id != "(name)":
            SyntaxError("Expected an attribute name.")
        self.first = left
        self.second = token
        advance()
        return self

""" AND LISTS """
# symbol(",", 150)
class Tok_Comma(Tok_Template):
    lbp = 150

# symbol("[", 150)
class Tok_LBrack(Tok_Template):
    lbp = 150
    def led(self, left):
        self.first = left
        self.second = expression()
        advance("]")
        return self
    def nud(self):
        self.first = []
        if token.id != "]":
            while 1:
                if token.id == "]":
                    break
                self.first.append(expression())
                if token.id != ",":
                    break
                advance(",")
        advance("]")
        return self

# symbol("(", 150)
class Tok_LParen(Tok_Template):
    lbp = 150
    def nud(self):
        expr = expression()
        # expect to see a right paren, if you don't, break
        advance(")")
        return expr
        '''HOW DO DISTINGUISH BETWEEN NUDS'''
    def nud(self):
        self.first = []
        comma = False
        if token.id != ")":
            while 1:
                if token.id == ")":
                    break
                self.first.append(expression())
                if token.id != ",":
                    break
                comma = True
                advance(",")
        advance(")")
        if not self.first or comma:
            return self # tuple
        else:
            return self.first[0]
    def led(self, left):
        self.first = left
        self.second = []
        if token.id != ")":
            while True:
                self.second.append(expression())
                if token.id != ",":
                    break
                advance(",")
        advance(")")
        return self

# symbol("=", 160)
class Tok_Assign(Tok_Template):
    lbp = 160
    def led (self, left):
        self.first = left
        self.second = expression(10)
        return self

# symbol("{", 170)
class Tok_LCBrace(Tok_Template):
    lbp = 170
    def nud(self):
        self.first = []
        if token.id != "}":
            while 1:
                if token.id == "}":
                    break
                self.first.append(expression())
                advance(":")
                self.first.append(expression())
                if token.id != ",":
                    break
                advance(",")
        advance("}")
        return self

'''WHAT DO I DO WITH ENDY THINGS'''
# symbol("]")
# symbol("}")
# symbol(";")
# symbol(",")

class Tok_Id(Tok_Template):
    '''does it need lbp?'''
    lbp = 10
    def nud (self):
        return self

class Tok_String(Tok_Template):
    def nud(self):
        return self 

class Tok_Numb(Tok_Template):
    def __init__(self, val):
        "SHOULD I MAKE THIS A FLOAT"
        self.val = int(val)
    def nud(self):
        return self

class Tok_End(Tok_Template):
        lbp = 0


def argument_list(list):
    while True:
        if token.id != "(name)":
            SyntaxError("Expected an argument name.")
        list.append(token)
        advance()
        if token.id == "=":
            advance()
            list.append(expression())
        else:
            list.append(None)
        if token.id != ",":
            break
        advance(",")

def constant(id):
    @method(symbol(id))
    def nud(self):
        self.id = "(literal)"
        self.value = id
        return self

    constant("None")
    constant("True")
    constant("False")


def makeTokenObj(token):
    
    # token = Tok_Template(tok.type, tok.value, tok.lexpos)



# Build the lexer
emcsqlexer = lex.lex()

# def tokenize():
emcsqlexer.input(input_script)


# Tokenizer

while True:
    tok = emcsqlexer.token()
    
    if not tok: break
    
    output.append(tok)
    list_tuples_form += [(tok.type, tok.value)]
    # pratt_obj_form.append(makeTokenObj(tok))
    token = Tok_Template(tok.type, tok.value, tok.lexpos)
    pratt_obj_form.append(token)
    if tok.type == 'STRING' or tok.type == 'NUMBER':
        constants_list += (tok.type, tok.value)
    # print tok.type, tok.value, tok.lexpos

# prints it in a way pratt parser could use
print pratt_obj_form
print constants_list


# def em_lexer(lexer,input_script):
#   pass
  