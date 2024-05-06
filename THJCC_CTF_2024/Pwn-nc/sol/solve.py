from pwn import *

r = remote('127.0.0.1', 30000)

r.sendlineafter(b'> ', b'Rick Astley')

r.interactive()
