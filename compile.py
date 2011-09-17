from compiler.ast import *
import compiler
import sys

global varlevel
varlevel = 1
global filelines1
filelines1=[]
global filelines
global filename
filename=[]
filelines=[]
global var
var=0
global listvar1
listvar1=[]

global count
count = 0
global stmtlist
stmtlist = []

def flaten(n):
	global count
	global listvar1
	if isinstance(n, Module):
		ast1 = flaten(n.node)
		flatenast = Module(None,Stmt(stmtlist))
		return flatenast
 
	elif isinstance(n, Stmt):
		[flaten(z) for z in n.nodes]
		return 1 
 
	elif isinstance(n, Printnl):
		tempprint = flaten(n.nodes[0])
		if isinstance(tempprint,str): 
			printnode = Printnl([Name(tempprint)],None)
		elif isinstance(tempprint,int): 
			printnode = Printnl([Const(tempprint)],None)
		stmtlist.append(printnode)
		return 1
 
	elif isinstance(n, Assign): 
		tempassign = flaten(n.expr)
		tempans = flaten(n.nodes[0])
		listvar1.append(str(tempans))
		if isinstance(tempassign,str):
			assnode = Assign(nodes=[AssName(name = tempans,flags='OP_ASSIGN')],expr=Name(tempassign))
		elif isinstance(tempassign,int):
			assnode = Assign(nodes=[AssName(name = tempans,flags='OP_ASSIGN')],expr=Const((tempassign))) 
		stmtlist.append(assnode)
		return 1 
 
	elif isinstance(n, AssName):
		return n.name
 
	elif isinstance(n, Discard):
		tempassign = flaten(n.expr)
		if isinstance(tempassign,int):
			discardnode = Discard(Const(tempassign))
		elif isinstance(tempassign,str):
			discardnode = Discard(Name(tempassign))
		stmtlist.append(discardnode)
		return 1
 
	elif isinstance(n, Const):
		return n.value
 
	elif isinstance(n, Name):
		return n.name
 
	elif isinstance(n, Add):
		templeft = flaten(n.left)
		tempright = flaten(n.right)
		tempans = "nh" + str(count)
		count+=1
		listvar1.append(str(tempans))
		if isinstance(templeft,str) and isinstance(tempright,str):
			addnode = Add((Name(templeft),Name(tempright)))
		elif isinstance(templeft,str) and isinstance(tempright,int):
			addnode = Add((Name(templeft),Const(tempright)))
		elif isinstance(templeft,int) and isinstance(tempright,int):
			addnode = Add((Const(templeft),Const(tempright))) 
		elif isinstance(templeft,int) and isinstance(tempright,str):
			addnode = Add((Const(templeft),Name(tempright)))
		assnode = Assign(nodes=[AssName(name=tempans,flags='OP_ASSIGN')],expr=addnode)
		stmtlist.append(assnode)
		return tempans
 
	elif isinstance(n, UnarySub):
		tempsub = flaten(n.expr)
		tempans = "nh" + str(count)
		count +=1  
		listvar1.append(str(tempans))
		if isinstance(tempsub,str): 
			subnode = UnarySub(Name(tempsub))
		elif isinstance(tempsub,int):
			subnode = UnarySub(Const(tempsub))
		assnode = Assign(nodes=[AssName(name=tempans,flags='OP_ASSIGN')],expr=subnode)   
		stmtlist.append(assnode)
		return tempans
 
	elif isinstance(n, CallFunc):
		tempans = "nh" + str(count)
		count += 1
		listvar1.append(str(tempans))
		funcnode = CallFunc(Name('input'),[],None,None)
		assnode = Assign(nodes=[AssName(name=tempans,flags='OP_ASSIGN')],expr=funcnode)
		stmtlist.append(assnode)
		return tempans
	else:
		raise Exception('Error in flaten: unrecognized AST node')

def convertx86(n):
	global varlevel
	global var
	global listvar1 
	global num
	if isinstance(n, Module):
		convertx86(n.node)
		return 1
	elif isinstance(n, Stmt):
		[convertx86(x) for x in n.nodes]
		pass
	elif isinstance(n, Printnl):
		temp = convertx86(n.nodes[0])
		if isinstance(temp,str):
			numtemp = listvar1.index(temp)
			numtemp = (numtemp+1)*4
			insval = str(numtemp)
			line = "	pushl -"+insval+"(%ebp)\n"
			filelines1.append(line)
			line = "	call print_int_nl\n"
			filelines1.append(line)
			line = "	addl $4, %esp\n"
			filelines1.append(line)
			filelines1.append("\n")
		else:
			line = "	pushl $" + str(temp)
			filelines1.append(line)
			filelines1.append("\n")
			line = "	call print_int_nl\n"
			filelines1.append(line)
			line = "	addl $4, %esp\n"
			filelines1.append(line)
			filelines1.append("\n")
		return 1
	elif isinstance(n, Assign):
		temp = convertx86(n.nodes[0])
		num = listvar1.index(temp)
		tempassign = convertx86(n.expr)
		if isinstance(tempassign,str):
			numtemp = listvar1.index(tempassign)
			numtemp = (numtemp +1)*4
			insval = str(numtemp)
			line = "	movl -"+insval+"(%ebp), %eax\n"
			filelines1.append(line)
			num1 = (num+1)*4  
			insval = str(num1)
			line = "	movl %eax, -"+insval+"(%ebp)\n" 	
			filelines1.append(line)
			filelines1.append("\n")
		elif isinstance(tempassign,int):
			num1 = (num+1)*4
			insval = str(num1)
			line = "	movl $"+str(tempassign)+", -"+insval+"(%ebp)\n"
			filelines1.append(line)
			filelines1.append("\n")
		return 1

	elif isinstance(n, AssName):
		return n.name
	elif isinstance(n, Discard):
		convertx86(n.expr)
		pass 
	elif isinstance(n, Const):
		return n.value
	elif isinstance(n, Name):
		return n.name
	elif isinstance(n, Add):
		temp1 = convertx86(n.left)
		temp2 = convertx86(n.right)
		if isinstance(temp1,int):
			if isinstance(temp2, int):
				line = "	movl $"+str(temp1)+", %eax\n"
				filelines1.append(line)
				filelines1.append("\n")
				line = "	addl $"+str(temp2)+", %eax\n"
				filelines1.append(line)
				num1 = (num+1)*4  
				insval = str(num1)
				line = "	movl %eax, -"+insval+"(%ebp)\n"
				filelines1.append(line)
				filelines1.append("\n")
			elif isinstance(temp2, str):
				numtemp = listvar1.index(temp2)
				numtemp  = (numtemp+1)*4
				insval = str(numtemp)
				line = "	movl -"+insval+"(%ebp), %eax\n" 
				filelines1.append(line)
				num1 = (num+1)*4  
				insval = str(num1)
				line = "	movl %eax, -"+insval+"(%ebp)\n"
				filelines1.append(line)
				line = "	addl $"+str(temp1)+", -"+insval+"(%ebp)\n"
				filelines1.append(line)
				filelines1.append("\n")
		elif isinstance(temp1,str):
			if isinstance(temp2,int):
				numtemp = listvar1.index(temp1)
				numtemp = (numtemp+1)*4
				insval = str(numtemp)
				line = "	movl -"+insval+"(%ebp), %eax\n"
				filelines1.append(line)
				num1 = (num+1)*4  
				insval = str(num1)
				line = "	movl %eax, -"+insval+"(%ebp)\n"
				filelines1.append(line)
				line = "	addl $"+str(temp2)+", -"+insval+"(%ebp)\n"
				filelines1.append(line)
				filelines1.append("\n")
			elif isinstance(temp2,str):
				numtemp = listvar1.index(temp1)
				numtemp = (numtemp+1)*4
				insval = str(numtemp)
				line = "	movl -" +insval+"(%ebp),%eax\n"
				filelines1.append(line)
				numtemp = listvar1.index(temp2)
				numtemp = (numtemp+1)*4
				insval = str(numtemp)
				line = "	addl -"+insval+"(%ebp), %eax\n"
				filelines1.append(line)
				num1 = (num+1)*4  
				insval = str(num1)
				line  = "	movl %eax, -" + insval + "(%ebp)\n"
				filelines1.append(line)
				filelines1.append("\n")   	
		pass

	elif isinstance(n, UnarySub):
		negval = convertx86(n.expr)
		if isinstance(negval,int):
			num1 = (num+1)*4  
			insval = str(num1)
			line = "	movl $"+str(negval)+", %eax\n"
			filelines1.append(line)
			line = "	movl %eax, -"+insval+"(%ebp)\n"
			filelines1.append(line)
			line = "	negl -"+insval+"(%ebp)\n"
			filelines1.append(line)
			filelines1.append("\n")
		elif isinstance(negval,str):
			numtemp = listvar1.index(negval)
			numtemp = (numtemp+1)*4
			insval = str(numtemp)
			line = "	movl -"+insval+"(%ebp), %eax\n"
			filelines1.append(line)
			num1 = (num+1)*4  
			insval = str(num1)
			line = "	movl %eax, -"+insval+"(%ebp)\n"
			filelines1.append(line)
			line = "	negl -"+insval+"(%ebp)\n"
			filelines1.append(line)
			filelines1.append("\n")
		pass

	elif isinstance(n, CallFunc):
		line = "	call input\n"
		filelines1.append(line)
		num1 = (num+1)*4  
		insval = str(num1)
		line = "	movl %eax, -"+insval+"(%ebp)\n"
		filelines1.append(line)
		filelines1.append("\n")
		pass
	else:
		raise Exception("Error in convert: unrecognized AST node")

def main(a1):
	import P0parser
	from P0parser import *
	#flatast = compiler.parseFile("inter.py")
	flatast = a1
	filelines1start =[]
	filelines1end = []
	filelines1start.append(".globl main")
	filelines1start.append("\n")
	filelines1start.append("main:\n")
	filelines1start.append("\n")
	var = len(listvar1)
	varalloc = var*4
	varstr = str(varalloc)
	filelines1start.append("	pushl %ebp\n")
	filelines1start.append("	movl %esp, %ebp\n")
	varalloc = var*4
	varstr = str(varalloc)
	line = "	subl $"+varstr+",%esp"
	filelines1start.append(line)
	filelines1start.append("\n")
	filelines1start.append("\n")
	temp =sys.argv[1]
	l = len(temp)
	temp = temp[:l-3]
	FILE = open(temp+".s","w")
	FILE.writelines(filelines1start)
	filelines1end.append("	movl $0, %eax")
	filelines1end.append("\n")
	filelines1end.append("	leave")
	filelines1end.append("\n")
	filelines1end.append("	ret")
	filelines1end.append("\n")
	a = convertx86(flatast)
	FILE.writelines(filelines1)
	FILE.writelines(filelines1end)
	FILE.close()  

def P0_Compiler():
	import P0parser
	from P0parser import *
	#ast = compiler.parseFile(sys.argv[1])
	ast  = my_parser(sys.argv[1])
	filelinesstart =[]
	a= flaten(ast) 
	main(a)
 
P0_Compiler()



