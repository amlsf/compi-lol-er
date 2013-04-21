import re

token_pat = re.compile("\s*(?:(\d+)|(\^|.))")

# token =  #must occur as global token is used
# token values are assigned and defined

# just an int in this int-stance
class NumToken:
	def __init__(self, value):
		self.value = int(value)
	def nud(self):
		return self
	# repr functions make it easier to see the resulting trees
	def __repr__(self):
		return "(num %s)" % self.value

# just the token +
class OpAddToken:
	lbp = 10
	def nud(self):
		self.first = expression(100)
		# has no second because it inserts a "unary add" node in the tree
		self.second = None
		return self
		# could be done with just: return expression(100)
	def led(self, left):
		self.first = left
		self.second = expression(10)
		return self
		# right = expression(10)
		# # return left + expression(10) # which returns just the value of the next token because its lbp is the same as rbp, not greater than
		# return left + right
	def __repr__(self):
		return "(add %s %s)" % (self.first, self.second)

class OpSubtToken:
	lbp = 10
	def nud(self):
		self.first = -expression(100)
		self.second = None
	def led(self, left):
		self.first = left
		self.second = -expression(10)
		return self
	def __repr__(self):
		return "(subtr %s %s)" % (self.first, self.second)

class OpMultToken:
	lbp = 20
	def led(self, left):
		self.first = left
		self.second = expression(20)
		return self
	def __repr__(self):
		return "(mult %s %s)" % (self.first, self.second)
	# def led(self, left):
	# 	return left * expression(20)

class OpDivToken:
	lbp = 20
	def led(self, left):
		self.first = left
		self.second = expression(20)
	def __repr__(self):
		return "(div %s %s)" % (self.first, self.second)

class OpPowToken:
	lbp = 30
	def led(self, left):
		# because the ^ is right-associative (binds to the number that is the power)
		# so if you delete 1 from rbp, 2^3^4 will be 2^(3^4) instead of (2^3)^4
		return left ** expression(30)

class EndToken:
	lbp = 0



def tokenize(program):
    for number, operator in token_pat.findall(program):
    	# print number, operator
        if number:
            yield NumToken(number)
        elif operator == "+":
            yield OpAddToken()
        elif operator == "-":
            yield OpSubtToken()
        elif operator == "*":
            yield OpMultToken()
        elif operator == "/":
            yield OpDivToken()
        elif operator == "^":
        	yield OpPowToken()
        else: raise SyntaxError("unknown operator")
    yield EndToken

def parse(program):
    global token, next
    next = tokenize(program).next
    token = next()
    return expression()



# pratt calls this "def parse"
def expression(rbp=0):
	# current token
	global token
	# t = current token (now considered previous token)
	t = token
	# make the current token the next one
	token = next()
	"If you're just accessing the value, is there no way to just ask for t.value without a specific method?"
	# leftd = denotation of the previous token
	left = t.nud()
	# until you reach a next token that has a denotation less than that of the most recent token, return leftd the leftd
	# "lbp is a vinding power controlling operator precedence; the higher the value, the tighter a token binds to the tokens that follow"
	while rbp < token.lbp:
		# when the lbp is higher than the previous token's binding power, continue on to the next token
		t = token
		token = next()
		# and call t.led(leftd)
		left = t.led(left)
	return left

print parse("1+2")
print parse("1+2*3")
# print parse("1+2-3*4/5")
# print parse("2^3^4") # = 2417851639... (not 4096)
# print parse("2^3") # = 8
# print parse("8^4") # = 4096