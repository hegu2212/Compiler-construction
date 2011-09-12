import ply.lex as lex

NAMEerved = {
	'input' : 'INPUT',
	'print' : 'PRINT'
}

tokens = ['INT','PLUS','LPAREN','RPAREN','MINUS','NAME','COMMENT','EQUALS']+list(NAMEerved.values())
t_PLUS = r'\+'
t_MINUS   = r'-'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_EQUALS  = r'='

def t_INT(t):
	r'\d+'
	try:
		t.value = int(t.value)
	except ValueError:
		print "integer value too large", t.value
		t.value = 0
	return t

def t_NAME(t):
	r'[a-zA-Z_][a-zA-Z_0-9]*'
	t.type = NAMEerved.get(t.value,'NAME')
	return t

def t_COMMENT(t):
    r'\#.*'
    pass

t_ignore = ' \t'

def t_newline(t):
	r'\n+'
	t.lexer.lineno += t.value.count("\n")

def t_error(t):
	print "Illegal character '%s'" % t.value[0]
	t.lexer.skip(1)

lexer=lex.lex()




