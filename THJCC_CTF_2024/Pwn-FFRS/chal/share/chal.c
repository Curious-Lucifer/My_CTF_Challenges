#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#pragma GCC optimize ("O0")

int main() {
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);

    char *flag = malloc(0x40);
    strcpy(flag, "THJCC{Th1s_i5_v3rY_mYst3r1ou$!_Why_d1d_you_g37_tHe_fl4g?!}");

    char remark[0x30] = {0};
    char name[0x30] = {0};
    char email[0x30] = {0};
    char check[0x10] = {0};

    puts("====== Free Flag Register System ======");
    puts("Register for a free flag lottery !!!");

    while (1) {
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