################################################################################
################################################################################
#######################        EMC[] TIME        ###############################
################################################################################
############################################ a compiler by emily gasca #########


from sys import argv
import ply.lex as lex
from peak.util.assembler import Code
from dis import dis

#vars for tokenizing
output = []
remain_tokens = []
constants_list = []
# list_tuples_form = []

#  vars for parsing
symbol_table={}
symbol_list = []
parse_tree = []
token = None
# keep scope object here
scope = None
# class Scope_Template(object):

# vars for compiling
c = Code()


# script, input_script = argvs

# input_script = '''
# var int | a = 10;
# var int | b = a * 3;
# log(b);
# var int | c = (b + 10) * 3;
# '''

# input_script = """
# if true {
#     log("Yay!");
# }
# """

# input_script = """
# int x = 5;
# if (x < 0) {
#     log("x is less than 0");
# }
# else {
#     log("x is greater than 0");
# }
# """

input_script = """log("hi");"""

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

################################################################################
################################################################################
#######################       LEXING  TIME       ###############################
################################################################################
################################################################################



# declaring token names for ply lexer to use, including reserved keywords
tokens = [
    'EMCSQ', 'SLCOMMENT', 'SEMICOLON', 'GLOBAL', 'STRING', 'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'LCBRACE', 'RCBRACE', 'DOT', 'COMMA', 'ARROWED', 'ASSIGN', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER', 'MODULO', 'LESS', 'GREATER', 'LESSEQ', 'GREATEQ', 'ISEQ', 'NOTEQ', 'ID','NUMBER',
    'USE', 'FUN', 'RETURN', 'CALL', 'ITEMIN', 'LOG', 'IF', 'ELIF', 'ELSE', 'OR', 'ORIF', 'AND', 'NOT', 'TYNONE', 'TYINT', 'TYSTRING', 'TYLIST', 'TYBOOL', 'TYMAP', 'TRUE', 'FALSE', 'EMPTY', 'BOUNDS', 'VAR', 'PIPE'
    ] #+ list(reserved.values())



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

# def t_SLCOMMENT(t):
#     r'//[^:][^\n]*'
#     pass

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
    # usually the left side in expressions
    first = None
    # usually the right side in expressions
    second = None
    # primarily for if, elses, etc
    third = None

    def __init__(self, type, value, pos):
        self.type = type
        self.value = value
        self.pos = pos
    def nulld(self):
        raise SyntaxError(
            "Syntax error when calling nulld for (%r)." % self.value
        )

    def leftd(self, left):
        raise SyntaxError(
            "Syntax error when calling leftd for (%r)." % self.value
        )

    def __repr__(self):
        return "(Type: %s; Value: '%s'; Position: %s)" % (self.type, self.value, self.pos)
        # if self.id == "(name)" or self.id == "(literal)":
        #     return "(%s %s)" % (self.id[1:-1], self.value)
        # out = [self.id, self.left_side, self.right_side, self.third]
        # out = map(str, filter(None, out))
        # return "(" + " ".join(out) + ")" # you know everything will be displayed in parentheses



##### CLASSES FOR BASIC STATEMENT TOKENS #####


class TokStatement(TokTemplate):
    def __init__(self, type, value, pos):
        self.type = type
        self.value = value
        self.pos = pos

class TokStatementList(TokStatement):
    def __init__(self, statements):
        self.statements = statements

    def eval(self):
        for stmt in self.statements:
            stmt.eval()

    def emit(self):
        for stmt in self.statements:
            stmt.emit()

class TokType(TokStatement):
    def __init__(self, type, value, pos):
        self.type = type
        self.value = value
        self.pos = pos    



##### CLASSES FOR END-Y TOKENS #####
class TokLast(TokTemplate):
    lbp = 0
    '''is this necessary to have \/ ??'''
    def leftd(self):
        pass
    def nulld(self):
        pass

class TokNewLine(TokTemplate):
    lbp = 0
    def leftd(self):
        pass
    def nulld(self):
        pass

class TokSemicolon(TokTemplate):
    lbp = 0
    def leftd(self):
        pass
    def nulld(self):
        pass

class TokRParen(TokTemplate):
    lbp = 0
    def leftd(self):
        pass
    def nulld(self):
        pass

class TokRBrack(TokTemplate):
    lbp = 0
    def leftd(self):
        pass
    def nulld(self):
        pass

class TokRCBrace(TokTemplate):
    lbp = 0
    def leftd(self):
        pass
    def nulld(self):
        pass

##### CLASSES FOR CONSTANT TOKENS #####
class TokId(TokTemplate):
    # '''does it need lbp?'''
    lbp = 0
    def nulld(self):
        symbol_list.append(self.value)
        return self
    def eval(self):
        symbol_list.append(self.value)
        return symbol_table[self.value]

class TokString(TokTemplate):
    def nulld(self):
        return self
    def eval(self):
        return self.value

class TokNumb(TokTemplate):
    lbp = 10
    def nulld(self):
        return self
    def eval(self):
        return self.value

class TokTrue(TokTemplate):
    def nulld(self):
        return self 
    def eval(self):
        return True

class TokFalse(TokTemplate):
    def nulld(self):
        return self 
    def eval(self):
        return False

class TokEmpty(TokTemplate):
    def nulld(self):
        return self 
    def eval(self):
        return None


##### CLASSES FOR EXPRESSION TOKENS #####

# infix_r("or", 30)
class TokOr(TokTemplate):
    lbp = 30

class TokOrif(TokTemplate):
    lbp = 30

# infix_r("and", 40)
class TokAnd(TokTemplate):
    lbp = 40

# followed by "in", "not in"
# infix_r("not", 50)
class TokNot(TokTemplate):
    lbp = 50
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 
    def eval(self):
        if self.first.eval() != self.second.eval():
            return True
        else:
            return False

# infix("in", 60)
class TokInNotIn(TokTemplate):
    lbp = 60

# infix("not", 60) # in, not in
class TokNotNotIn(TokTemplate):
    lbp = 60    
    def leftd(self, left):
        if token.id != "in":
            raise SyntaxError("Invalid syntax")
        advance()
        self.id = "not in"
        self.first = left
        self.second = expression(60)
        return self
        lbp = 60

# infix("<", 60);
class TokLess_Than(TokTemplate):
    lbp = 60
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self
    def eval(self):
        if self.first.eval() < self.second.eval():
            return True
        else:
            return False

# infix("<=", 60)
class TokLess_Or_Eq(TokTemplate):
    lbp = 60
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 
    def eval(self):
        if self.first.eval() <= self.second.eval():
            return True
        else:
            return False

# infix(">", 60) 
class TokGreater_Than(TokTemplate):
    lbp = 60
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 
    def eval(self):
        if self.first.eval() >= self.second.eval():
            return True
        else:
            return False

# infix(">=", 60)
class TokGreater_Or_Eq(TokTemplate):
    lbp = 60
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 
    def eval(self):
        if self.first.eval() >= self.second.eval():
            return True
        else:
            return False

# infix("!=", 60); 
class TokNot_Eq(TokTemplate):
    lbp = 60
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 
    def eval(self):
        if self.first.eval() != self.second.eval():
            return True
        else:
            return False

# infix("==", 60)
class TokIs_Equal(TokTemplate):
    lbp = 60
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 
    def eval(self):
        if self.first.eval() == self.second.eval():
            return True
        else:
            return False    

# infix("+", 110) 
class TokPlus(TokTemplate):
    lbp = 90
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self
    def eval(self):
        return self.first.eval() + self.second.eval()

# infix("-", 110)
class TokMinus(TokTemplate):
    lbp = 90
    def nulld(self):
        return -expression(110)
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self
    def eval(self):
        return self.first.eval() - self.second.eval()

# infix("*", 120) 
class TokTimes(TokTemplate):
    lbp = 90
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self
    def eval(self):
        return self.first.eval() * self.second.eval()


# infix("/", 120)
class TokDiv(TokTemplate):
    lbp = 90
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 
    def eval(self):
        return self.first.eval() / self.second.eval()

# infix("%", 120)
class TokModulo(TokTemplate):
    lbp = 90
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self     
    def eval(self):
        return self.first.eval() % self.second.eval()



# infix_r("^", 140)
class TokPower(TokTemplate):
    lbp = 130
    def leftd(self, left):
        self.first = left
        self.second = expression(lbp-1)
        return self 
    def eval(self):
        return self.first.eval() % self.second.eval()



##### CLASSES FOR HIGH-BINDING POWER TOKENS #####

# symbol("[", 150)
class TokLBrack(TokTemplate):
    lbp = 150
    def leftd(self, left):
        self.first = left
        self.second = expression()
        advance("]")
        return self
    def nulld(self):
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
    def nulld(self):
        expr = expression()
        # expect to see a right paren, if you don't, break
        advance(TokRParen)
        return expr
        '''HOW DO DISTINGUISH BETWEEN nulldS'''
    # def nulld(self):
    #     self.first = []
    #     comma = False
    #     if token.value != ")":
    #         while 1:
    #             if token.value == ")":
    #                 break
    #             self.first.append(expression())
    #             if token.value != ",":
    #                 break
    #             comma = True
    #             advance(",")
    #     advance(")")
    #     if not self.first or comma:
    #         return self # tuple
    #     else:
    #         return self.first[0]
    def leftd(self, left):
        self.first = left
        self.second = []
        if token.value != ")":
            while True:
                self.second.append(expression())
                if token.value != ",":
                    break
                advance(",")
        advance(")")
        return self

# symbol("=", 160)
class TokAssign(TokTemplate):
    lbp = 160
    def leftd (self, left):
        self.first = left
        self.second = expression(10)
        advance(TokSemicolon)
        return self
    def eval(self):
        symbol_table[self.first] = self.second.eval()
        print "Set", self.first, "to", self.second.eval()
        return


# symbol("{", 170)
class TokLCBrace(TokTemplate):
    lbp = 170
    def nulld(self):
        self.first = []
        if token.type != "}":
            while 1:
                if token.type == "}":
                    break
                self.first.append(expression())
                advance(":")
                self.first.append(expression())
                if token.type != ",":
                    break
                advance(",")
        advance("}")
        return self

'''WHAT DO I DO WITH ENDY THINGS'''
# symbol("]")
# symbol("}")



##### CLASSES FOR STATEMENT TOKENS #####


# symbol("->", 140)
class TokArrowed(TokStatement):
    lbp = 140

""" HOW DOES DOT NOTATION WORK """
# symbol(".", 150)
class TokDot(TokStatement):
    lbp = 150
    def leftd(self, left):
        if token.type != "ID":
            SyntaxError("Expected an attribute identifier.")
        self.first = left
        self.second = token
        advance()
        return self

""" AND LISTS """
# symbol(",", 150)
class TokComma(TokStatement):
    lbp = 150

class TokGlobal(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass        

class TokPipe(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass

##### CLASSES FOR STATEMENT TOKENS -- RESERVED #####

class TokUse(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokFunction(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokReturn(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokCall(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokItemIn(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokLog(TokStatement):
    def stmtd(self):
        advance(TokLog) # skip past 'log'
        advance(TokLParen) # skip past l paren
        self.first = expression(0)
        advance(TokRParen)
        advance(TokSemicolon)
        global token
        print "tok-loggin:", token.type
        return self

    def eval(self):
        print self.first.eval()

    def emit(self):
        c.LOAD_CONST(self.first.eval())
        c.PRINT_ITEM()
        c.PRINT_NEWLINE()
        c.LOAD_CONST(None)
        c.RETURN_VALUE()

# symbol("if", 20) 
# ternary form
class TokIf(TokStatement):
    def stmtd(self):
        pass
        # evaluate the conditional
        # if conditional true, 
        advance('elif')
    def eval(self):
        pass
# symbol("if", 20) 
# ternary form
class TokElif(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass

# symbol("if", 20) 
# ternary form
class TokElse(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokBounds(TokStatement):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokVar(TokStatement):
    def stmtd(self):
        global symbol_list
        advance(TokVar)
        advance(TokType)
        advance(TokPipe)
        '''add ID to official symbol table/list now or when you walk through the tree?'''
        # add ID to symbol list so you can use it during assignment
        symbol_list += token.value
        print "added %s to the symbol_list" % token.value
        # send the rest into expression
        self.first = expression(0)
        advance(TokSemicolon)
        return self
    def eval(self):
        pass



##### CLASSES FOR TYPE TOKENS #####

class TokTypeNone(TokType):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokTypeInt(TokType):
    def stmtd(self):
        return
    def eval(self):
        pass

class TokTypeString(TokType):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokTypeList(TokType):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokTypeBool(TokType):
    def stmtd(self):
        pass
    def eval(self):
        pass

class TokTypeMap(TokType):
    def stmtd(self):
        pass
    def eval(self):
        pass


# METHODS FOR CAPTURING REGEX TOKENS, MAKING OBJECTS

# METHODS FOR EXPRESSION TOKENS


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

def t_STRING(t):
    r'("[^"]*")'  # |(\'[^']*\')' # must have line count
    t = TokString(t.type, t.value, t.lexpos)
    return t

def t_TRUE(t):
    r'true'
    t = TokTrue(t.type, t.value, t.lexpos)
    return t

def t_FALSE(t):
    r'false'
    t = TokFalse(t.type, t.value, t.lexpos)
    return t
    
def t_EMPTY(t):
    r'empty'
    t = TokEmpty(t.type, t.value, t.lexpos)
    return t

def t_SEMICOLON(t):
    r';'
    t = TokSemicolon(t.type, t.value, t.lexpos)
    return t

def t_GLOBAL(t):
    r'\\/'
    t = TokGlobal(t.type, t.value, t.lexpos)
    return t


def t_LPAREN(t):
    r'\('
    t = TokLParen(t.type, t.value, t.lexpos)
    return t

def t_RPAREN(t):
    r'\)'
    t = TokRParen(t.type, t.value, t.lexpos)
    return t

def t_LBRACK(t):
    r'\['
    t = TokLBrack(t.type, t.value, t.lexpos)
    return t

def t_RBRACK(t):
    r'\]'
    t = TokRBrack(t.type, t.value, t.lexpos)
    return t

def t_LCBRACE(t):
    r'\{'
    t = TokLCBrace(t.type, t.value, t.lexpos)
    return t

def t_RCBRACE(t):
    r'\}'
    t = TokRCBrace(t.type, t.value, t.lexpos)
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

def t_USE(t):
    r'use'
    t = TokUse(t.type, t.value, t.lexpos)
    return t

def t_FUN(t):
    r'fun'
    t = TokFunction(t.type, t.value, t.lexpos)
    return t

def t_RETURN(t):
    r'return'
    t = TokReturn(t.type, t.value, t.lexpos)
    return t

def t_CALL(t):
    r'call'
    t = TokCall(t.type, t.value, t.lexpos)
    return t

def t_ITEMIN(t):
    r'itemin'
    t = TokItemIn(t.type, t.value, t.lexpos)
    return t

def t_LOG(t):
    r'log'
    t = TokLog(t.type, t.value, t.lexpos)
    return t

def t_IF(t):
    r'if'
    t = TokIf(t.type, t.value, t.lexpos)
    return t

def t_ELIF(t):
    r'elif'
    t = TokElif(t.type, t.value, t.lexpos)
    return t

def t_ELSE(t):
    r'else'
    t = TokElse(t.type, t.value, t.lexpos)
    return t

def t_TYINT(t):
    r'int'
    t = TokTypeInt(t.type, t.value, t.lexpos)
    return t

def t_TYSTRING(t):
    r'string'
    t = TokTypeString(t.type, t.value, t.lexpos)
    return t

def t_TYLIST(t):
    r'list'
    t = TokTypeList(t.type, t.value, t.lexpos)
    return t

def t_TYBOOL(t):
    r'bool'
    t = TokTypeBool(t.type, t.value, t.lexpos)
    return t

def t_TYMAP(t):
    r'map'
    t = TokTypeMap(t.type, t.value, t.lexpos)
    return t

def t_TYNONE(t):
    r'none'
    t = TokTypeNone(t.type, t.value, t.lexpos)

def t_VAR(t):
    r'var'
    t = TokVar(t.type, t.value, t.lexpos)
    return t

def t_PIPE(t):
    r'\|'
    t = TokPipe(t.type, t.value, t.lexpos)
    return t

##### ID DEF MUST COME LAST SO RESERVED WORDS CAUGHT FIRST #####

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # t.type = reserved.get(t.value,'ID')
    t = TokId(t.type, t.value, t.lexpos)
    return t

def argument_list(list):
    while True:
        if token.type != "ID":
            SyntaxError("Expected an argument identifier.")
        list.append(token)
        advance()
        if token.type == "=":
            advance()
            list.append(expression())
        else:
            list.append(None)
        if token.value != ",":
            break
        advance(",")

def constant(id):
    @method(symbol(id))
    def nulld(self):
        self.id = "(literal)"
        self.value = id
        return self

    constant("None")
    constant("True")
    constant("False")




################################################################################
################################################################################
#######################       PARSING TIME       ###############################
################################################################################
################################################################################


def em_lexer(): # lexer,input_script):
    global remain_tokens
    global constants_list
    global symbol_list
    global symbol_list
    # Build the lexer
    emcsqlexer = lex.lex()
    # def tokenize():
    emcsqlexer.input(input_script)
    # Tokenizer
    while True:

        tok = emcsqlexer.token()
        
        if not tok: break
        
        # construct list of token objects to be parsed
        remain_tokens.append(tok)

        # construct constants
        if tok.type == 'STRING' or tok.type == 'NUMBER':
            constants_list += (tok.type, tok.value)

        # construct symbols
        if tok.type == 'ID':
            symbol_list.append(tok.value)
            if tok.value not in symbol_table:
                symbol_table[tok.value] = tok.type
        # print tok.type, tok.value, tok.lexpos


# Printing pretty tokenized creations
def display_lexing():
    print "Raw EMC[] input: \n", input_script
    print "\n\nTokens: \n",remain_tokens
    print "\n\nIn symbol table:"
    for key, value in symbol_table.iteritems():
        print key
    print "\n\nList of constants: \n", constants_list, "\n\n"



##### METHODS FOR PARSING PROCESS #####

class Program(object):
    def stmtd(self):
        # all the baby statement lists
        self.chilluns = statement_list() 
        return self

    def eval(self):
        # iterates through the list of statement
        for child in self.chilluns:
            child.eval()

    def emit(self):
        for child in self.chilluns:
            child.emit()




# debugging counter to see how many iterations have run
depth = 0
def parse():
    # set token to first of whole program
    advance()
    p = Program()
    p.stmtd()
    return p

def statement_list():
    statements = []
    # make list, each item of which is either a statement or an expression
    while not isinstance(token, TokLast):
        statements.append(statement())
    return statements

def statement():
    # if token is statement, run it's statement denotation
    if isinstance(token, TokStatement):
        return token.stmtd()
    # otherwise run the expression function
    return expression(0)


# nulld doesn't care about the tokens to left
    # nulld --> variables, literals, prefix op
# leftd cared about tokens to left
    # infix ops, suffix ops
# pratt calls this "def parse"
def expression(rbp=0):
    # t = current token (now considered previous token)
    t = token
    print "left is: ", t
    # make token the next one in the program
    advance()
    print "right is ", token
    # leftd = denotation of the previous token
    left = t.nulld()
    # until you reach a next token that has a denotation less than that of the most recent token, return the leftd
    # "lbp is a vinding power controlling operator precedence; the higher the value, the tighter a token binds to the tokens that follow"
    print "rbp: ", rbp, "token.lbp: ", token.lbp 
    while (token.type != 'SEMICOLON') and (rbp < token.lbp):
        # when the lbp is higher than the previous token's binding power, continue expression to core of highest precedence
        # set prev token to the token with higher lbp
        t = token
        # move token on
        advance()
        # and call t.leftd to do whatever that high precedenced thing was going to do the expression
        left = t.leftd(left)
    print "returning", left
    return left

def advance(token_type=None):
    global token
    if token_type and not isinstance(token, token_type):
        raise SyntaxError("Expected %r, got %r" % (token_type, token.__class__))
    token = next()
    return token

def next():
    # all this purely for debugging/watching flow of parsing
    global depth
    global token
    if depth > 0:
        print "Depth, Method, Token", depth, "next-ed, starting with", token.type
    depth += 1

    global remain_tokens
    if remain_tokens:
        # pop off the next token obj in the list and return it so it gets set to the global 'token'
        return remain_tokens.pop(0)
    else:
        # makes 
        return TokLast('last', 'last', 'end')


################################################################################
################################################################################
#######################       COMPILER TIME      ###############################
################################################################################
################################################################################



def compile_prog():
    program.emit()
    dis(c.code())

if __name__ == "__main__":
    em_lexer()
    display_lexing()
    program = parse()
    print "OMG ITS RUNNING. Parse ish:\n"
    program.eval()
    print "\n\nNow that we've evaluated, let's compile: \n"
    compile_prog()

