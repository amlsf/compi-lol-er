# from http://norvig.com/lispy.html tutorial
# mostly done to understand the process, not to create something new.

# interprets lisp program in python

isa = isinstance

# Evaluate an expression in an enviornment.
# x is a tuple: (keyword, expression) or (keyword)
def eval(x, env=global_env):
	# what is the type Symbol defined as? must import?
	if isa(x, Symbol): # is a variable reference
		return env.find(x)[x]
	elif not isa(x, list): # is a constant literal
		return x
	elif x[0] == 'quote': # is a quote expression
		# WHAT'S HAPPENING HERE?! x is a tuple??
		# x = ('quote', expression)
		# so does underscore just take 'quote' and exp gets set to the expression?
		(_, exp) = x
		# is returning x[1] not the same?
		return exp 
	elif x[0] == 'if':
		(_, test, conseq, alt) = x # if conditional then___ else___
		# so is this ('if', ())
		"""HOW does eval(test,env) return a boolean? or is it just if it exists?"""
		# call eval(conditional,env) 
		# if :
		#	conseq
		# else
		#	alt
		# call eval on whatever that returns
		return eval((conseq if eval(test,env) else alt), env)
	elif x[0] == 'set!':
		(_, var, exp) = x
		# env is dictionary so
		env.find(var)[var] = eval(exp, env)
	# adds symbol/value binding!!
	elif x[0] == 'define':
		(_, var, exp) = x
		env[var] = eval(exp, env)
	# adds symbol/value binding!!
	elif x[0] == 'lambda':
		(_, vars, exp) = x # lambda (var*) exp
		"Why does lambda get followed by *args"?!
		return lambda *args: eval(exp, Env(vars, args, env))
	elif x[o] == 'begin':
		for exp in x[1:]:
			val = eval(exp, env) #begin exp*
		return val
	""" (proc exp*) huh???"""
	else:
		"""x is a list?! so evaluate each one...what is this for?"""
		exps = [eval(exp, env) for exp in x] 
		proc = exps.pop0
		return proc(*exps)
