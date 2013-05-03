from peak.util.assembler import Code
from dis import dis

'''WHAT SHOULD I KEEP TRACK OF'''
const_tacker = 0
var_tracker = 0
symbol_table = {}

'''KEEP TRACK OF ALL CONSTANTS FROM ORIGINAL LEXING, PASS TO COMPILER'''

# c = Code()
# c.set_lineno(15) # set the current line number (optional)
# c.LOAD_CONST(42)
# c.STORE_FAST('x')
# c.RETURN_VALUE()

# print dis(c.code())

def setx(num):
	x = num
	return x

	# emc[] equiv:
	# fun (int num) -> setx -> int {
	# 	int x = num;
	# 	return x;
	# }

	# dis(setx):
	# LOAD_FAST 0 (num) # loads whatever constant is locally in space 0, puts it on top of the stack
	# STORE_FAST 1 (x) # stores TOS in space 1, which is "where x is"
	# LOAD_FAST 1 (x) # loads whatever's in space 1 to TOS
	# RETURN_VALUE # returns TOS

def printx(var):
	print var
	return

	# emc[] equiv:
	# fun (int num) -> printx -> int {
	# 	log(var);
	# 	return;
	# }

	# dis(printx):
	# LOAD_FAST 0 (var) # gets var by finding it in list of variables
	# PRINT_ITEM
	# PRINT_NEWLINE
	# LOAD_CONST 0 (None) #returns none
	# RETURN_VALUE

def start():
	y = setx(5)
	printx(y)

	# emc[] equiv:
	# fun () -> start -> int {
	# 	int y = setx(5);
	# 	printx(y);
	# }

	# dis(start):
	# LOAD_GLOBAL 0 (setx)
	# LOAD_CONST 1 (5)
	# CALL_FUNCTION 1
	# STORE_FAST 0 (y)
	# LOAD_GLOBAL 1 (printx)
	# LOAD_FAST 0 (y)
	# CALL_FUNCTION 1
	# POP_TOP
	# LOAD_CONST 0 (None)
	# RETURN_VALUE

def start2():
	printx(setx(5))

	# emc[] equiv:
	# fun () -> setx -> int {
	# 	int x = num;
	# 	return x;
	# }

	# dis (start2):
	# LOAD_GLOBAL 0 (printx) 
	# LOAD_GLOBAL 1 (setx)
	# LOAD_CONST 1 (5)
	# CALL_FUNCTION 1
	# CALL_FUNCTION 1
	# POP_TOP
	# LOAD_CONST 0 (None)
	# RETURN_VALUE


'''
	def makeList():
...     a= []
...     b = [1,2,3]
...     a += ['a','b']
...     a += ['c']
...     b += a
...     return b
... 
>>> dis(makeList)
  2           0 BUILD_LIST               0
              3 STORE_FAST               0 (a)

  3           6 LOAD_CONST               1 (1)
              9 LOAD_CONST               2 (2)
             12 LOAD_CONST               3 (3)
             15 BUILD_LIST               3
             18 STORE_FAST               1 (b)

  4          21 LOAD_FAST                0 (a)
             24 LOAD_CONST               4 ('a')
             27 LOAD_CONST               5 ('b')
             30 BUILD_LIST               2
             33 INPLACE_ADD         
             34 STORE_FAST               0 (a)

  5          37 LOAD_FAST                0 (a)
             40 LOAD_CONST               6 ('c')
             43 BUILD_LIST               1
             46 INPLACE_ADD         
             47 STORE_FAST               0 (a)

  6          50 LOAD_FAST                1 (b)
             53 LOAD_FAST                0 (a)
             56 INPLACE_ADD         
             57 STORE_FAST               1 (b)

  7          60 LOAD_FAST                1 (b)
             63 RETURN_VALUE      
'''