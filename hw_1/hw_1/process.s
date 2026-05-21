	.arch armv8-a
	.file	"process.cpp"
	.text
	.align	2
	.global	process
	.type	process, %function
process:
.LFB0:
	.cfi_startproc
	mov	x4, x0
	cmp	w1, 0
	ble	.L4
	mov	x2, 0
	mov	w0, 0
.L3:
	ldr	w3, [x4, x2, lsl 2]
	add	w0, w0, w3
	add	x2, x2, 1
	cmp	w1, w2
	bgt	.L3
.L1:
	ret
.L4:
	mov	w0, 0
	b	.L1
	.cfi_endproc
.LFE0:
	.size	process, .-process
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
