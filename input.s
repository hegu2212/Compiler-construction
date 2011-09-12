.globl main
main:

	pushl %ebp
	movl %esp, %ebp
	subl $4,%esp

	movl $3, %eax

	addl $4, %eax
	movl %eax, -4(%ebp)

	pushl -4(%ebp)
	call print_int_nl
	addl $4, %esp

	movl $0, %eax
	leave
	ret
