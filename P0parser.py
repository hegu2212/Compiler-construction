from compiler.ast import *

precedence = (
('nonassoc','PRINT'),
('left','PLUS','MINUS')
)

def p_module(t):
    'module : stmt_list'
    t[0] = Module(None, Stmt(t[1]))

def p_empty_list(t):
    'stmt_list : '
    t[0] = []

def p_extend_list(t):
    'stmt_list : statement stmt_list'
    t[0] = [t[1]] + t[2]
	
def p_print_statement(t):
	'statement : PRINT expression'
	t[0] = Printnl([t[2]], None)

def p_assign_expression(t):
	'statement : NAME EQUALS expression'
	t[0] = Assign([AssName(name=t[1],flags='OP_ASSIGN')], expr=(t[3]))

def p_discard_statement(t):
    'statement : expression'
    t[0] = Discard(t[1])	
	
def p_plus_expression(t):
    'expression : expression PLUS expression'
    t[0] = Add((t[1], t[3]))

def p_minus_expression(t):
    'expression : MINUS expression'
    t[0] = UnarySub((t[2]))


def p_int_expression(t):
	'expression : INT'
	t[0] = Const(t[1])

def p_name(t):
		'expression : NAME'
		t[0] = Name(t[1])
		
def p_input_function(t):
	'expression : INPUT LPAREN RPAREN'
	t[0] = CallFunc(Name('input'),[],None,None)



def p_paran_expression(t):
	'expression : LPAREN expression RPAREN'
	t[0] = t[2]



# Print this statement for syntax errors
def p_error(t):
    print "Syntax errot at '%s'"%t.value

# Build the parser
def my_parser(inputfile):
	import ply.yacc as yacc
	from P0lexer import tokens
	parser = yacc.yacc()
	f = open(inputfile)
	result = parser.parse(f.read())
	f.close()
	return result
 
