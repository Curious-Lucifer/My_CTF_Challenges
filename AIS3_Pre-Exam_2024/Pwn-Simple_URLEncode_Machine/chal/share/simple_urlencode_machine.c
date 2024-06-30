#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>

#define MAX_INPUT_SIZE 0xff
#define MAX_FLAG_SIZE 0xff

char flag[MAX_FLAG_SIZE + 1];
char input_buf[MAX_INPUT_SIZE + 1];
char output_buf[3 * MAX_INPUT_SIZE + 1];


void init() {
    setvbuf(stdin, 0, 2, 0);
    setvbuf(stdout, 0, 2, 0);

    int fd = open("/home/chal/flag", O_RDONLY);
    read(fd, flag, MAX_FLAG_SIZE);
    close(fd);
}


int is_reserved_character(char chr) {
    char unreserved_character_list[] = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', \
                                        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', \
                                        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '_', '.', '~', '$'};
    for (int i = 0; i < 67; i++) {
        if (chr == unreserved_character_list[i])
            return 0;
    }
    return 1;
}


void urlencode(char *src, ssize_t length, char *target) {
    for (int i = 0, j = 0; i < length; i++) {
        if (is_reserved_character(src[i])) {
            snprintf(target + j, 5, "%%%%%02x", src[i] & 0xff);
            j += 4;
        } else {
            target[j] = src[i];
            j++;
        }
    }
}


void oracle() {
    char buf[4 * MAX_INPUT_SIZE + 1];
    ssize_t length;

    length = read(0, input_buf, MAX_INPUT_SIZE);
    if (length < 0) {
        exit(-1);
    }

    urlencode(input_buf, length, buf);
    snprintf(output_buf, 3 * MAX_INPUT_SIZE + 1, buf);
}


int main() {
    init();

    puts("+-------- Simple URLEncode Machine --------+");
    puts("|                                          |");
    puts("|   URL encode everything you input !!!    |");
    puts("|                                          |");
    puts("|------------------------------------------+");

    while (1) {
        puts("|");
        puts("| What do you what to encode ?");
        printf("| > ");
        oracle();
        printf("| > %s\n", output_buf);
    }

    return 0;
}