import emcsq_pratt_lexer
from emcsq_pratt_lexer import pratt_obj_form as imported_tokens

# token =  #must occur as global token is used
# token values are assigned and defined

symbol_table={}
parse_tree = []
token = None
# keep scope object here
scope = None

# class Scope_Template(object):


def next():
    if imported_tokens:
        return imported_tokens.pop(0)
    else:
        # makes 
        return LastToken()

def parse(program):
    global token
    global depth
    # grabs first token off front of list
    token = next()
    # statements = [] # do i need this?!
    while not isinstance(token, TokLast):
        if isinstance(token, TokStatement):
            print "-----STATEMENT FOUND-----"
            print "Depth, Method, Token", depth, "stmt-ed", token.type
            depth += 1
            element = token.stmtd()
            # token.stmtd()
        else:
            print "-----EXPR FOUND-----"
            element = expression()
            # expression()
        statements.append(element)
    all_stmts = StatementList(statements) # but whhyyy
    all_stmts.eval()
    


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
