# Pwn - Simple URLEncode Machine

## Solution

首先去分析 `simple_urlencode_machine.c`，可以發現在第 58 行

```c
    snprintf(output_buf, 3 * MAX_INPUT_SIZE + 1, buf);
```

這裡有一個 FMT，接著看一下要怎麼操控 buf

```c
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
```

可以知道兩件事第一件是 `buf` 是從 `input_buf` 中 url encode 而來，第二件事是 `buf` 並不會清零。

再來研究一下 `urlencode` 這個 function

```c
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
```

可以發現就是把保留字元變成 `%%??` 這種形式，其中 `??` 是兩個十六進位的數字，而這個 `%%` 就是之後在 `oracle` 中 `sprintf` 時會變成 `%` 的 format string。

在往下仔細看 `is_reserved_character`，可以發現 `$` 這個字符被歸為未保留字符（實際上 `$` 是保留字符）

整理一下上面的資訊，可以知道 FMT 的構造方式就是先輸入一個保留字元架上 `$p` 或是 `$s` 之類的字串，讓 `urlencode` 把它變成 `%%??$p` 或 `%%??$s` 這種格式，然後第二次的時候因為 `buf` 內容不會被清掉，所以可以把第一次的 `%%??` 的第一個 `%` 蓋成其他字元，如果控制 `??` 是數字的話，就可以變成 `%??$p` 或 `%??$s` 這種 format string 了。

能構造 format string 之後就是想辦法拿到 flag，我這邊是利用寫 argv chain 來寫 flag 的 address 到 stack 上，然後印出 flag。

