# Pwn - FFRS - Revenge

## 小記
這題還蠻酷的，是唯一一題賽中完全沒有人解出來的題目，直接變成防破台題。

---
## Solution

首先可以看一下 `run.sh`，可以發現跑的時候會把檔名是 flag 的 shared library 給 `LD_PRELOAD` 進來。

```shell
LD_PRELOAD=/home/chal/THJCC\{Th1s_fl4G_i5n\'7_fr3E,_bU7_It\'s_f0r_You\!\!\!\}.so timeout 60 /home/chal/chal
```

另外再看一下 `chal.c`，可以看到一個 `clean_envp` 的函數

```c
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

    ...
}
```

原本用 `LD_PRELOAD` 進來的 shared library 也是一個 environment variable，但這個函數把它清掉了，所以也沒有辦法從這邊拿到 flag。

這邊需要知道一個 structure 叫做 `link_map`

```c
struct link_map
{
    ElfW(Addr) l_addr;                // Difference between the address in the ELF file and the addresses in memory.
    char *l_name;                     // Absolute file name object was found in.
    ElfW(Dyn) *l_ld;                  // Dynamic section of the shared object.
    struct link_map *l_next, *l_prev; // Chain of loaded objects.

    ...
};
```

這個 double link list 會把每一個載進來的 shared library 資料都串起來，其中的 `l_name` 就是 shared library 的檔案名稱。而因為這個 binary 是 Partial RELRO，所以 `.got.plt + 8` 的位址的值會指向 `link_map` 的第一個 node。所以我們只要先知道 codebase 來計算出 `.got.plt`，就可以一個一個 node 找，其中一個 node 就會是檔案名是 flag 的 node。

知道要怎麼做之後仔細和一下 `chal.c`，可以發現第 59 行

```c
        printf(remark);
```

有一個很明顯的 FMT，所以可以直接利用 FMT 來 leak 各種值，只是需要注意的是 fortify 有被打開，所以只能用一般的 `%p` 或 `%s` 這種，不能用 `%10$s` 這種 format。

把 FMT 一個一個疊好之後就是一個一個值去 leak 然後就可以拿到 flag 了。