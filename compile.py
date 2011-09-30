from compiler.ast import *
import compiler
import sys

global filelines1
filelines1=[]
global filelines
global filename
filename=[]
filelines=[]
global listvar1
listvar1=[]
global num
num = 0
global count
count = 0
global stmtlist
stmtlist = []
global instlist
instlist = []

class movl(Node):
	def __init__(self,src,dest):
		self.src = src
		self.dest = dest
	def __repr__(self):
		return "movl(%s, %s)" %(repr(self.src), repr(self.dest))

class addl(Node) :
	def __init__(self,left,right):
		self.left = left
		self.right = right
	def __repr__(self):
		return "addl(%s, %s)" %(repr(self.left), repr(self.right))

class negl(Node):
	def __init__(self,expr):
		self.expr = expr
	def __repr__(self):
		return "negl(%s)" %(repr(self.expr))

class pushl(Node):
	def __init__(self,expr):
		self.expr = expr
	def __repr__(self):
		return "pushl(%s)" %(repr(self.expr))

class call(Node):
	def __init__(self,func,dest):
		self.func = func
		self.dest = dest
	def __repr__(self):
		return "call(%s,%s)" %(repr(self.func),repr(self.dest))

def flaten(n):
	global count
	global listvar1
	if isinstance(n, Module):
		ast1 = flaten(n.node)
		flatenast = Module(None,Stmt(stmtlist))
		return flatenast
 
	elif isinstance(n, Stmt):
		[flaten(x) for x in n.nodes]
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
	global listvar1 
	global num
	global irname

	if isinstance(n, Module):
		convertx86(n.node)
		return 1
	elif isinstance(n, Stmt):
		[convertx86(x) for x in n.nodes]
		pass
	elif isinstance(n, Printnl):
		temp = convertx86(n.nodes[0])
		if isinstance(temp,str):
			printnode = call('print_int_nl',temp)
			instlist.append(printnode)
		else:
			printnode = call('print_int_nl',temp)
			instlist.append(printnode)
		return 1
	elif isinstance(n, Assign):
		temp = convertx86(n.nodes[0])
		irname = temp
		tempassign = convertx86(n.expr)
		if isinstance(tempassign,str):
			assnode = movl(src=tempassign, dest=temp)
			instlist.append(assnode)

		elif isinstance(tempassign,int):		
			assnode = movl(src=tempassign, dest=temp)
			instlist.append(assnode)
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
		if isinstance(temp1,int)and isinstance(temp2, int):			
			addnode = movl(src = temp1,dest = 'accu')
			instlist.append(addnode)
			addnode = addl(left = temp2,right='accu')
			instlist.append(addnode)
			addnode = movl(src = 'accu',dest = irname)
			instlist.append(addnode)

		elif isinstance(temp1,int) and isinstance(temp2, str):
			addnode = addl(left = temp1, right = temp2)
			instlist.append(addnode)
			addnode = movl(src = temp2,dest = irname)
			instlist.append(addnode)

		elif isinstance(temp1,str) and isinstance(temp2,int):
			addnode = addl(left = temp2, right = temp1)
			instlist.append(addnode)
			addnode = movl(src = temp1, dest = irname)
			instlist.append(addnode)

		elif isinstance(temp1,str) and isinstance(temp2,str):
			addnode = movl(src = temp1, dest = irname)
			instlist.append(addnode)
			addnode = addl(left = temp2,right = irname)
			instlist.append(addnode)  	
		pass

	elif isinstance(n, UnarySub):
		negval = convertx86(n.expr)
		if isinstance(negval,int):
			unarynode = movl(src = negval, dest = irname)
			instlist.append(unarynode)
			unarynode = negl(irname)
			instlist.append(unarynode)

		elif isinstance(negval,str):
			unarynode = negl(negval)
			instlist.append(unarynode)
			unarynode = movl(src = negval, dest = irname)
			instlist.append(unarynode)
		pass

	elif isinstance(n, CallFunc):
		callnode = call('input',dest=irname)
		instlist.append(callnode)
		pass
	else:
		raise Exception("Error in convert: unrecognized AST node")

def intergraph(l,i,u):
	livelist = l 
	instlist = i
	unspillable = u
	instlist.reverse()
	livelist.reverse()
	templist = []
	interference = {}
	print instlist, '\n'
	print livelist

	for x in instlist:
		if isinstance(x,addl):
			temp = []
			temp.append(x.right)
			indexnum = instlist.index(x) + 1
			templist = livelist[indexnum]
			templist = set(templist) - set(temp)
			if (x.right in interference.keys()):
				joinlist = templist | set(interference[x.right])
				interference[x.right] = list(joinlist)
			else:
				interference[x.right] = list(templist)
			
		if isinstance(x, movl):
			temp = []
			temp.append(x.src)
			temp.append(x.dest)
			indexnum = instlist.index(x) + 1
			templist = livelist[indexnum]
			templist = set(templist) - set(temp)
			print templist
			if (x.dest in interference.keys()):
				joinlist = templist | set(interference[x.dest])
				interference[x.dest] = list(joinlist)
			else:
				interference[x.dest] = list(templist)
			for y in templist:
				if (y in interference.keys()):
					temp = []
					temp.append(x.dest)
					interference[y] = list(set(interference[y]) | set(temp))
				else:
					temp = []
					temp.append(x.dest)
					interference[y] = list(set(temp))

		if isinstance(x, negl):
			temp = []
			temp.append(x.expr)
			indexnum = instlist.index(x) + 1
			templist = livelist[indexnum]
			templist = set(templist) - set(temp)
			if (x.expr in interference.keys()):
				joinlist = templist | set(interference[x.expr])
				interference[x.expr] = list(joinlist)
			else:
				interference[x.expr] = list(templist)

		if isinstance(x, call):
			temp = []
			temp.append(x.dest)
			indexnum = instlist.index(x) + 1
			templist = livelist[indexnum]
			templist = set(templist) - set(temp)
			if (x.dest in interference.keys()):
				joinlist = templist | set(interference[x.dest])
				interference[x.dest] = list(joinlist | set(['%eax','%ecx','%edx']))
			else:
				interference[x.dest] = list(templist | set(['%eax','%ecx','%edx']))
			
			for y in templist:
				if (y in interference.keys()):
					interference[y] = list(set(interference[y]) | set(['%eax','%ecx','%edx']))
				else:
					interference[y] = list(set(['%eax','%ecx','%edx']))


	print "\n",interference,"\n"
	color(interference, instlist, unspillable)

def color(a, i, u):
	interference = a
	instlist = i
	unspillable = u
	coloredlist = []
	keylist = interference.keys()
	varcolor = {}
	splist = []
	spindex = 0
	flag = 0
	print keylist
	#print unspillable, '\n'
	while (len(keylist) > 0):
		reglist = ['%eax','%ebx','%ecx','%edx','%esi','%edi']
		saturlist2 = []
		for x in keylist:
			if (x in unspillable):
				flag = 1
				tempx = x
			saturlist = set(interference[x]) - set(coloredlist)
			saturlist2.append(len(saturlist))
		keyindex = saturlist2.index(min(saturlist2))
		if (flag ==1):
			neighbours = interference[tempx]
			flag = 0
		else:
			neighbours = interference[keylist[keyindex]] 
		for y in neighbours:
			if (y == '%eax' or y == '%ecx' or y == '%edx'):
				temp = []
				temp.append(y)
				reglist = list(set(reglist) - set(temp))

			else:
				if (y in varcolor.keys()):
					temp = []
					temp.append(varcolor[y])
					print temp
					reglist = list(set(reglist) - set(temp))
					#print reglist
		if (len(reglist)>0):
			varcolor[keylist[keyindex]] = reglist[0]
		else:
			spvar = 'sp'+str(spindex)
			varcolor[keylist[keyindex]] = spvar
			spindex = spindex + 1
			splist.append(spvar)
		coloredlist.append(keylist[keyindex])
		keylist.remove(keylist[keyindex])

	print varcolor
	spill(instlist, splist, varcolor)

def spill(i,s,v):
	instlist = i
	instlist1 = instlist
	splist = s
	varcolor = v
	global num
	unspillable = []
	for x in instlist:
		if isinstance(x, addl):
			if isinstance(x.left,str):
				left = varcolor[x.left]
				right = varcolor[x.right]
				if (left in splist) and (right in splist):
					insertpos = instlist.index(x)
					insertpos1 = insertpos + 1
					temp = "xxtmp"+str(num)
					num = num + 1
					instruction = movl(x.left, temp)
					instruction1 = addl(temp, x.right)
					instlist.remove(x)
					instlist.insert(insertpos, instruction)
					instlist.insert(insertpos1, instruction1)
					unspillable.append(temp)
		if isinstance(x, movl):
			if isinstance(x.src, str):
				src = varcolor[x.src]
				dest = varcolor[x.dest]
				if (src in splist) and (dest in splist):
					insertpos = instlist.index(x)
					insertpos1 = insertpos + 1
					temp = "xxtmp"+str(num)
					instruction = movl(x.src, temp)
					instruction1 = movl(temp, x.dest)
					num = num + 1
					instlist.remove(x)
					instlist.insert(insertpos, instruction)
					instlist.insert(insertpos1, instruction1)
					unspillable.append(temp)
	
	if len(unspillable)>0:
		livevar(instlist, unspillable)
	else:
		colorx86(instlist, varcolor, splist)


def colorx86(i,v,s):
	instlist = i
	varcolor = v
	splist = s
	for inst in instlist:
		if isinstance(inst,movl):
			if isinstance(inst.src, str):
				inst.src = varcolor[inst.src]
			if isinstance(inst.dest, str):
				inst.dest = varcolor[inst.dest]
		elif isinstance(inst, addl):
			if isinstance(inst.left, str):
				inst.left = varcolor[inst.left]
			if isinstance(inst.right, str):
				inst.right = varcolor[inst.right]
		elif isinstance(inst, call):
			inst.dest = varcolor[inst.dest]
		elif isinstance(inst, negl):
			if isinstance(inst.expr, str):
				inst.expr = varcolor[inst.expr]
	#print '\n', instlist
	finalx86(instlist, splist)

def finalx86(i,s):
	instlist = i
	splist = s
	line = []
	line.append(".globl main\n")
	line.append("main:\n")
	line.append("\n")
	line.append("	pushl %ebp\n")
	line.append("	movl %esp, %ebp\n")
	varalloc = len(splist)*4
	if (varalloc > 0):
		varstr = str(varalloc)
		line.append("	subl $"+varstr+",%esp\n")
	#print instlist
	for inst in instlist:
		if isinstance(inst, movl):
			src = inst.src
			dest = inst.dest
			if (src in splist):
				srcindex = splist.index(src)
				insvar = (srcindex + 1)*4
				src = "-"+str(insvar)+"(%ebp)"
			if (dest in splist):
				srcindex = splist.index(dest)
				insvar = (srcindex + 1)*4
				dest = "-"+str(insvar)+"(%ebp)"

			if isinstance(src,int):
				line.append("	movl $"+str(src)+", "+dest+" \n")
			else:
				line.append("	movl "+src+", "+dest+" \n")

		if isinstance(inst, addl):
			left = inst.left
			right = inst.right
			if(left in splist):
				srcindex = splist.index(left)
				insvar = (srcindex + 1)*4
				left = "-"+str(insvar)+"(%ebp)"
			if (right in splist):
				srcindex = splist.index(right)
				insvar = (srcindex + 1)*4
				right = "-"+str(insvar)+"(%ebp)"

			if isinstance(left, int):
				line.append("	addl $"+str(left)+", "+right+"\n")
			else:
				line.append("	addl "+left+", "+right+"\n")

		if isinstance(inst, negl):
			expr = inst.expr
			if(expr in splist):
				srcindex = splist.index(expr)
				insvar = (srcindex + 1)*4
				expr = "-"+str(insvar)+"(%ebp)"
			line.append("	negl "+expr+"\n")
		
		if isinstance(inst, call):
			name = inst.func
			if (name == "input"):
				line.append("	call input\n")
				dest = inst.dest
				if (dest in splist):
					srcindex = splist.index(dest)
					insvar = (srcindex + 1)*4
					dest = "-"+str(insvar)+"(%ebp)"
				line.append("	movl %eax, "+dest+"\n")
			else:
				dest = inst.dest
				if (dest in splist):
					srcindex = splist.index(dest)
					insvar = (srcindex + 1)*4
					dest = "-"+str(insvar)+"(%ebp)"
				line.append("	pushl "+dest+"\n")
				line.append("	call print_int_nl\n")
				line.append("	addl $4, %esp\n")

	line.append("	movl $0, %eax\n")
	line.append("	leave\n")
	line.append("	ret\n")

	temp =sys.argv[1]
	l = len(temp)
	temp = temp[:l-3]
	FILE = open(temp+".s","w")
	FILE.writelines(line)
	FILE.close() 


def livevar(i, u):
	instlist = i
	unspillable = u
	livelist=[]
	currentset = []
	#print instlist,'\n'
	livelist.append(currentset)
	reverselist = instlist
	reverselist.reverse()
	#print reverselist
	for x in reverselist:
		if isinstance(x, addl):
			temp = []
			temp.append(x.right)
			currentset = set(currentset) - set(temp)
			if isinstance((x.left), int):
				currentset = set(currentset) | set(temp)
			else:
				temp.append(x.left)
				currentset = set(currentset) | set(temp)
			livelist.append(list(currentset))
	
		elif isinstance(x, movl):
			temp =[]
			temp.append(x.dest)
			currentset = set(currentset) - set(temp)
			if isinstance((x.src),str):
				temp = []
				temp.append(x.src)
				currentset = set(currentset) | set(temp)
			livelist.append(list(currentset))

		elif isinstance(x,negl):
			temp = []
			temp.append(x.expr)
			currentlist = set(currentset) - set(temp)
			livelist.append(list(currentset))

		elif isinstance(x, call):
   			temp =[]
			temp.append(x.dest)
			if (x.func=='input'):
				currentset = set(currentset) - set(temp)
			else:
				currentset = set(currentset) | set(temp)
			livelist.append(list(currentset))

		elif isinstance(x, pushl):
			temp = []
			temp.append(x.expr)
			currentset = set(currentset) | set(temp)
			livelist.append(list(currentset))

	#print livelist
	intergraph(livelist,instlist, unspillable)
	
def main(a1):
	#flatast = compiler.parseFile("inter.py")
	unspillable = []
	flatast = a1
	#print flatast,"/n"
	a = convertx86(flatast)
	livevar(instlist, unspillable) 

def P0_Compiler():
	ast = compiler.parseFile(sys.argv[1])
	filelinesstart =[]
	a= flaten(ast) 
	main(a)
 
P0_Compiler()



