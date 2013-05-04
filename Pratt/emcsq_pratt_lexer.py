from sys import argv
import ply.lex as lex

#vars for tokenizing
output = []
pratt_obj_form = []
constants_list = []
# list_tuples_form = []

#  vars for parsing
symbol_table={}
parse_tree = []
token = None
# keep scope object here
scope = None
# class Scope_Template(object):


# script, input_script = argvs

# input_script = "a = 10 + 2 b = a * 3 log(b) c = (b + 10) * 3"

input_script = """
if True {
    log("Yay!");
}
"""

# input_script = """
# int x = 5;
# if (x < 0) {
#     log("x is less than 0");
# }
# else {
#     log("x is greater than 0");
# }
# """

# input_script = """
# //: please ignore
# this ://
# \/ list listA = [1,2,3,4,5];
# \/ int num1 = 20;
# \/ int num2 = 10;

# fun (int x, int y) -> funName -> int {
#     call listThing itemin listA(-2){
#         if listThing > 0) {
#             y = 283 + -29 * listThing;
#             return "some string here" + x;
#         }
#     }
# }

# (num1, num2) --> funName;
# """


# reserved words so the longest regex (ID) isn't used first and wrongly captured as an ID token
reserved = {
    'use' : 'USE',
    'fun' : 'FUN',
    'return' : 'RETURN',
    'call' : 'CALL',
    'itemin' : 'ITEMIN',
    'log' : 'LOG',
    'if' : 'IF',
    'elif' : 'ELIF',
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
    'none' : 'NONE',
    'bounds' : 'BOUNDS',
    'start' : 'START'
}

# declaring token names, including reserved keywords
tokens = [
    'EMCSQ', 'SLCOMMENT', 'SEMICOLON', 'GLOBAL', 'STRING', 'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'LCBRACE', 'RCBRACE', 'DOT', 'COMMA', 'ARROWED', 'ASSIGN', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER', 'MODULO', 'LESS', 'GREATER', 'LESSEQ', 'GREATEQ', 'ISEQ', 'NOTEQ', 'ID','NUMBER',
    ] + list(reserved.values())



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

"""EASTER EGG SHENANIGANS...do I want to allow anything to be written within the brackets? If so, what happens with that?"""
# def t_EMCSQ(t):
#     r'EmC\[\]'
#     return t



##### CLASS FOR BASIC TOKEN #####

class TokTemplate(object):
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
        # out = [self.id, self.left_side, self.right_side, self.third]
        # out = map(str, filter(None, out))
        # return "(" + " ".join(out) + ")" # you know everything will be displayed in parentheses



##### CLASS FOR BASIC STATEMENT TOKENS #####


class TokStatement(TokTemplate):
    def __init__(self, value):
        self.value = value


class TokStatementList(TokStatement):
    def __init__(self, statements):
        self.statements = statements

    def std(self):
        pass

    def eval(self):
        for stmt in self.statements:
            stmt.eval()


##### CLASSES FOR EXPRESSION TOKENS #####


class TokLast(TokTemplate):
    lbp = 0
    '''is this necessary to have \/ ??'''
    def led(self):
        pass
    def nud(self):
        pass

class TokNewLine(TokTemplate):
    pass

class TokSemicolon(TokTemplate):
    lbp = 0

class TokId(TokTemplate):
    # '''does it need lbp?'''
    # lbp = 10
    def nud (self):
        return self

class TokString(TokTemplate):
    def nud(self):
        return self 

class TokNumb(TokTemplate):
    def nud(self):
        return self



# infix_r("or", 30)
class TokOr(TokTemplate):
    lbp = 30

class TokOrif(TokTemplate):
    lbp = 30

# infix_r("and", 40)
class TokAnd(TokTemplate):
    lbp = 40

# infix_r("not", 50)
class TokNot(TokTemplate):
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
class TokIn(TokTemplate):
    lbp = 60

# infix("not", 60) # in, not in
class TokNot_In(TokTemplate):
    lbp = 60

# infix("is", 60) # is, is not
class TokIs(TokTemplate):
    lbp = 60

# infix("<", 60);
class TokLess_Than(TokTemplate):
    lbp = 60
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self

# infix("<=", 60)
class TokLess_Or_Eq(TokTemplate):
    lbp = 60
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 

# infix(">", 60) 
class TokGreater_Than(TokTemplate):
    lbp = 60
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 

# infix(">=", 60)
class TokGreater_Or_Eq(TokTemplate):
    lbp = 60
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 

# infix("!=", 60); 
class TokNot_Eq(TokTemplate):
    lbp = 60
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 

# infix("==", 60)
class TokIs_Equal(TokTemplate):
    lbp = 60

# infix("+", 110) 
class TokPlus(TokTemplate):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self
    "WHAT DO I DO WITH THIS"
    # symbol(id, bp).led = led

# infix("-", 110)
class TokMinus(TokTemplate):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self

# infix("*", 120) 
class TokTimes(TokTemplate):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self

# infix("/", 120)
class TokDiv(TokTemplate):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 

# infix("%", 120)
class TokModulo(TokTemplate):
    lbp = 90
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self     

# prefix("-", 130) 
class TokNegative(TokTemplate):
    lbp = 90

# infix_r("^", 140)
class TokPower(TokTemplate):
    lbp = 130
    def led(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 


# symbol("[", 150)
class TokLBrack(TokTemplate):
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
class TokLParen(TokTemplate):
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
class TokAssign(TokTemplate):
    lbp = 160
    def led (self, left):
        self.first = left
        self.second = expression(10)
        return self

# symbol("{", 170)
class TokLCBrace(TokTemplate):
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



##### CLASSES FOR STATEMENT TOKENS #####

# symbol("\/", 135)
class TokGlobal(TokTemplate):
    lbp = 135

# symbol("->", 140)
class TokArrowed(TokTemplate):
    lbp = 140

""" HOW DOES DOT NOTATION WORK """
# symbol(".", 150)
class TokDot(TokTemplate):
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
class TokComma(TokTemplate):
    lbp = 150


##### CLASSES FOR STATEMENT TOKENS -- RESERVED #####

class TokUse(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokFunction(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokReturn(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokCall(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokItemIn(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokLog(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

# symbol("if", 20) 
# ternary form
class TokIf(TokTemplate):
    def stmtd():
        pass
    def eval(self):
        pass
# symbol("if", 20) 
# ternary form
class TokElif(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

# symbol("if", 20) 
# ternary form
class TokElse(TokTemplate):
    def stmtd():
        pass
    def eval(self):
        pass

class TokTypeNone(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokTypeInt(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokTypeString(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokTypeList(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokTypeBool(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokTypeMap(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokTrue(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokFalse(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokTypeEmpty(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokTypeStart(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass

class TokTypeBounds(TokTemplate):
    def stmtd():
        pass
    def eval():
        pass


# METHODS FOR CAPTURING REGEX TOKENS, MAKING OBJECTS

# METHODS FOR EXPRESSION TOKENS
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'ID')
    t = TokId(t.type, t.value, t.lexpos)
    return t

def t_NUMBER(t):
    r'-?((\d+(\.\d+)?)|(\.\d+))' # should include neg/pos either '[nums]' or '[numss].[nums]' or '.[nums]''
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.fvalue)
        t.value = 0
    # return float(t)
    t = TokNumb(t.type, t.value, t.lexpos)
    return t


def t_SLCOMMENT(t):
    r'//[^:][^\n]*'
    pass

def t_SEMICOLON(t):
    r';'
    t = TokTemplate(t.type, t.value, t.lexpos)
    return t

def t_GLOBAL(t):
    r'\\/'
    t = TokGlobal(t.type, t.value, t.lexpos)
    return t

def t_STRING(t):
    r'("[^"]*")'  # |(\'[^']*\')' # must have line count
    t = TokString(t.type, t.value, t.lexpos)
    return t

def t_LPAREN(t):
    r'\('
    t = TokLParen(t.type, t.value, t.lexpos)
    return t

def t_RPAREN(t):
    r'\)'
    t = TokTemplate(t.type, t.value, t.lexpos)
    return t

def t_LBRACK(t):
    r'\['
    t = TokLBrack(t.type, t.value, t.lexpos)
    return t

def t_RBRACK(t):
    r'\]'
    t = TokTemplate(t.type, t.value, t.lexpos)
    return t

def t_LCBRACE(t):
    r'\{'
    t = TokLCBrace(t.type, t.value, t.lexpos)
    return t

def t_RCBRACE(t):
    r'\}'
    t = TokTemplate(t.type, t.value, t.lexpos)
    return t

def t_DOT(t):
    r'\.'
    t = TokDot(t.type, t.value, t.lexpos)
    return t

def t_COMMA(t):
    r','
    t = TokComma(t.type, t.value, t.lexpos)
    return t

def t_ARROWED(t):
    r'->'   # or '-->' ?
    t = TokArrowed(t.type, t.value, t.lexpos)
    return t

def t_ISEQ(t):
    r'=='
    t = TokIs_Equal(t.type, t.value, t.lexpos)
    return t

def t_ASSIGN(t):
    r'='
    t = TokAssign(t.type, t.value, t.lexpos)
    return t

def t_PLUS(t):
    r'\+'
    t = TokPlus(t.type, t.value, t.lexpos)
    return t

def t_MINUS(t):
    r'-'
    t = TokMinus(t.type, t.value, t.lexpos)
    return t

def t_TIMES(t):
    r'\*'
    t = TokTimes(t.type, t.value, t.lexpos)
    return t

def t_DIVIDE(t):
    r'/'
    t = TokDiv(t.type, t.value, t.lexpos)
    return t

def t_POWER(t):
    r'\^'
    t = TokPower(t.type, t.value, t.lexpos)
    return t

def t_MODULO(t):
    r'%'
    t = TokModulo(t.type, t.value, t.lexpos)
    return t

def t_LESS(t):
    r'<'
    t = TokLess_Than(t.type, t.value, t.lexpos)
    return t

def t_GREATER(t):
    r'>'
    t = TokGreater_Than(t.type, t.value, t.lexpos)
    return t

def t_LESSEQ(t):
    r'<='
    t = TokLess_Or_Eq(t.type, t.value, t.lexpos)
    return t

def t_GREATEQ(t):
    r'>='
    t = TokGreater_Or_Eq(t.type, t.value, t.lexpos)
    return t

def t_NOTEQ(t):
    r'!='
    t = TokNot_Eq(t.type, t.value, t.lexpos)
    return t


##### METHODS FOR STATEMENT TOKENS #####

# def t_IF(t):
#     r'if'
#     t = TokIf(t.type, t.value, t.lexpos)
#     return t




##### ACTUAL LEXING USING PLY #####


# Build the lexer
emcsqlexer = lex.lex()

# def tokenize():
emcsqlexer.input(input_script)


# Tokenizer

while True:
    tok = emcsqlexer.token()
    
    if not tok: break
    
    # output.append(tok)
    # list_tuples_form += [(tok.type, tok.value)]
    pratt_obj_form.append(tok)
    # token = TokTemplate(tok.type, tok.value, tok.lexpos)
    # pratt_obj_form.append(token)
    if tok.type == 'STRING' or tok.type == 'NUMBER':
        constants_list += (tok.type, tok.value)
    # print tok.type, tok.value, tok.lexpos

# prints it in a way pratt parser could use
print pratt_obj_form
print constants_list


# def em_lexer(lexer,input_script):
#   pass



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



##### METHODS FOR PARSING PROCESS #####

def next():
    if remain_tokens:
        # pop off the next token obj in the list and return it so it gets set to the global 'token'
        return remain_tokens.pop(0)
    else:
        # makes 
        return LastToken()

def parse(program):
    global token
    # grabs next token off front of list
    token = next()
    statements = []
    while not isinstance(token, LastToken):
        if isinstance(token, TokStatement):
            element = token.stmtd()
        else:
            element = expression()
            # how do you force a newlinetoken?
            # next(NewLineToken)
        statements.append(element)
    all_stmts = StatementList(statements)


# NUD doesn't care about the tokens to left
    # nud --> variables, literals, prefix op
# LED cared about tokens to left
    # infix ops, suffix ops
# pratt calls this "def parse"
def expression(rbp=0):
    global token
    # t = current token (now considered previous token)
    t = token
    print t
    # make token the next one in the program
    token = next()
    "If you're just accessing the value, is there no way to just ask for t.value without a specific method?"
    # leftd = denotation of the previous token
    left = t.nud()
    print token
    # until you reach a next token that has a denotation less than that of the most recent token, return the leftd
    # "lbp is a vinding power controlling operator precedence; the higher the value, the tighter a token binds to the tokens that follow"
    while rbp < token.lbp:
        # when the lbp is higher than the previous token's binding power, continue on to the next token
        t = token
        token = next()
        # and call t.led(leftd)
        left = t.led(left)
    return left
