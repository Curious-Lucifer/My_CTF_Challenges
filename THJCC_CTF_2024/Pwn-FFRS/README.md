# Pwn - FFRS

## 小記
這題因為 Pwn 題已經夠多了，所以就沒有在比賽的時候放出來，但我已經出了，所以想說一並放出來。

---
## Solution
分析一下 `chal.c`，可以發現第 40 行

```c
        printf(remark);
```

有一個很明顯的 FMT，然後在第 11 - 12 行的時候

```c
    char *flag = malloc(0x40);
    strcpy(flag, "THJCC{Th1s_i5_v3rY_mYst3r1ou$!_Why_d1d_you_g37_tHe_fl4g?!}");
```

可以看到把 flag 放進 `malloc` 出來的空間，然後這個空間的 address 就在 stack 上。稍微找一下就可以找到這個 address 存在 `rsp + 8`，所以用 `%7$s` 就可以把 flag 印出來了。

