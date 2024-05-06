#include <stdio.h>
#include <string.h>
#include <seccomp.h>


void clean_envp(char **envp) {
    int idx = 0;
    char *buf = envp[idx++];
    while (buf) {
        char *chr_ptr = buf;
        while (*chr_ptr) {
            *(chr_ptr++) = 0;
        }
        buf = envp[idx++];
    }
}


int main(int argc, char **argv, char **envp) {
    clean_envp(envp);

    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);

    scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_KILL);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit_group), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(exit), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(read), 0);
    seccomp_rule_add(ctx, SCMP_ACT_ALLOW, SCMP_SYS(write), 0);
    seccomp_load(ctx);
    seccomp_release(ctx);

    char remark[0x30] = {0};
    char name[0x30] = {0};
    char email[0x30] = {0};
    char check[0x10] = {0};

    puts("====== Free Flag Register System ======");
    puts("Register for a free flag lottery !!!");

    for (int i = 0; i < 5; i++) {
        memset(email, 0, sizeof(email));
        memset(name, 0, sizeof(name));
        memset(remark, 0, sizeof(remark));
        memset(check, 0, sizeof(check));

        puts("=======================================");
        printf("Email  > ");
        scanf("%47s", email);
        printf("Name   > ");
        scanf("%47s", name);
        printf("Remark > ");
        scanf("%47s", remark);

        puts("=======================================");
        printf("Email  : %s\n", email);
        printf("Name   : %s\n", name);
        printf("Remark : ");
        printf(remark);

        printf("\nIs everything corret ? [Y/n] ");
        read(0, check, 0x2);

        if ((check[0] == 'Y') || (check[0] == 'y')) 
            break;
    }

    return 0;
}