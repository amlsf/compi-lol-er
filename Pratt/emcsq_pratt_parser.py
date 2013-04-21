# token =  #must occur as global token is used
"wait so are all these tokens made during the tokenization process? and if so then does it occur in the same .py file or a different ~lexing~ script?"
# token values are assigned and defined

class symbol_base(object):
    id = None # node/token type name
    value = None # only used by "literals", numbers
    first = second = third = None # initializing tree nodes

    def nud(self):
        raise SyntaxError(
            "Syntax error (%r)." % self.id
        )

    def led(self, left):
        raise SyntaxError(
            "Syntax error (%r)." % self.id
        )

    def __repr__(self):
        if self.id == "(name)" or self.id == "(literal)":
            return "(%s %s)" % (self.id[1:-1], self.value)
        out = [self.id, self.first, self.second, self.third]
        out = map(str, filter(None, out))
        return "(" + " ".join(out) + ")" # you know everything will be displayed in parentheses



# TOKEN TYPE FACTORY
symbol_table={}

# takes token identifier and binding power (optional), creates new class if necessary.
# binding power defaults to 0, (for nums, end, etc.)
def symbol(id, bp=0):
    try:
        s = symbol_table[id]
    except KeyError:
        class s(symbol_base):
            pass
        s.__name__ = "symbol-" + id # for debugging
        s.id = id
        s.lbp = bp
        symbol_table[id] = s
    else:
        s.lbp = max(bp, s.lbp)
    return s

def infix(id, bp):
    def led(self, left):
        self.first = left
        self.second = expression(bp)
        return self
    "NOT TOTALLY CLEAR ON WHAT'S HAPPENING IN THIS LINE"
    "this changed from symbol("+") to symbol(id, bp) so why is that different?"
    symbol(id, bp).led = led

def infix_r(id, bp):
    def led(self, left):
        self.first = left
        self.second = expression(bp-1)
        return self
    symbol(id, bp).led = led

def prefix(id, bp):
    def nud(self):
        self.first = expression(bp)
        self.second = None
        return self
    symbol(id).nud = nud

def nud(self):
    print "PARENNNNNNs"
    expr = expression()
    print token
    advance(")")
    return expr
symbol("(").nud = nud

def advance(id=None):
    global token
    print "id, tokenid %r %r"%(id, token.id)
    if id and token.id != id:
        print "BARF"
        raise SyntaxError("Expected %r" % id)
    token = next()

symbol("lambda", 20)
symbol("if", 20) # ternary form

infix_r("or", 30)
infix_r("and", 40)
infix_r("not", 50)

infix("in", 60)
infix("not", 60) # in, not in
infix("is", 60) # is, is not
infix("<", 60); infix("<=", 60)
infix(">", 60); infix(">=", 60)
infix("<>", 60)
infix("!=", 60); infix("==", 60)

infix("|", 70)
infix("&", 90)

infix("<<", 100); infix(">>", 100)

infix("+", 110); infix("-", 110)
infix("*", 120); infix("/", 120)
infix("%", 120);
infix("//", 120)

prefix("-", 130); prefix("+", 130)
prefix("~", 130)
infix_r("^", 140)

symbol(".", 150)
symbol("[", 150); symbol("(", 150)

# fitted with nud method that returns symbol itself, uses lambda
symbol("(literal)").nud = lambda self: self
symbol("(name)").nud = lambda self: self
symbol("(end)")
symbol(")")

# so you can use decorators
# def method(s):
#     assert issubclass(s, symbol_base)
#     def bind(fn):
#         setattr(s, fn.__name__, fn)
#         return bind

# @method(symbol("("))
# def nud(self):
#     expr = expression()
#     advance(")")
#     return expr

# symbol("(").nud = nud

# tokenizer part that is language-specific to turn source into literals, names, and operators
def tokenize_lang(program):
    import tokenize
    from cStringIO import StringIO
    type_map = {
        tokenize.NUMBER: "(literal)",
        tokenize.STRING: "(literal)",
        tokenize.OP: "(operator)",
        tokenize.NAME: "(name)",
    }
    for t in tokenize.generate_tokens(StringIO(program).next):
        try:
            yield type_map[t[0]], t[1]
        except KeyError:
            if t[0] == tokenize.ENDMARKER:
                break
            else:
                raise SyntaxError("Syntax error")
    yield "(end)", "(end)"

#SPLIT TWO PARSER FUNCTIONS FOR DEBUGGING/USING SECOND PART FOR OTHER SYNTAXES

# checks both operators and names against the symbol table (to handle keyword operators) and uses psuedo-symbol ("(name)") for all other names
def tokenize(program):
    for id, value in tokenize_lang(program):
        # if number or string
        if id == "(literal)":
            # set bp value via dictionary mapping from "literal" key
            symbol = symbol_table[id]
            # make class for this 
            s = symbol()
            s.value = value
        # else if name or operator
        else:
            symbol = symbol_table.get(value)
            if symbol:
                s = symbol()
            elif id == "(name)":
                symbol = symbol_table[id]
                s = symbol()
                s.value = value
            else:
                raise SyntaxError("Unknown operator (%r)" % id)
        yield s


def parse(program):
    global token, next
    # is this being used like an object?
    # tokenize(program) yields generator of symbols
    next = tokenize(program).next
    token = next()
    return expression()

depth = 0

# pratt calls this "def parse"
def expression(rbp=0):
    d = depth
    print d
    global depth
    depth += 1
    # current token
    global token
    # t = current token (now considered previous token)
    t = token
    print t
    # make the current token the next one
    token = next()
    "If you're just accessing the value, is there no way to just ask for t.value without a specific method?"
    # leftd = denotation of the previous token
    left = t.nud()
    print d
    print token
    # until you reach a next token that has a denotation less than that of the most recent token, return leftd the leftd
    # "lbp is a vinding power controlling operator precedence; the higher the value, the tighter a token binds to the tokens that follow"
    while rbp < token.lbp:
        # when the lbp is higher than the previous token's binding power, continue on to the next token
        t = token
        token = next()
        # and call t.led(leftd)
        left = t.led(left)
    return left

# print parse("1+2")
# print parse("1+2-3*4/5")
print parse("(1+2-3)*4/5")
# print parse("2^3^4") # = 2417851639... (not 4096)
# print parse("2^3") # = 8
# print parse("8^4") # = 4096
# print parse("'hello'+'world'")
