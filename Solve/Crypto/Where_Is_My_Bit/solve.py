
def un_bitshift_right_xor(value: int, shift: int):
    """
    - input : `value (int)`, `shift (int)`
    - output : `result (int)` , `value = (result >> shift) ^ result`
    """

    i = 0
    result = 0
    while ((i * shift) < 32):
        partmask = int('1' * shift + '0' * (32 - shift), base = 2) >> (shift * i)
        part = value & partmask
        value ^= (part >> shift)
        result |= part
        i += 1
    return result

def un_bitshift_left_xor_mask(value: int, shift: int, mask: int):
    """
    - input : `value (int)`, `shift (int)`, `mask (int)`
    - output : `result (int)` , `value = ((result << shift) & mask) ^ result`
    """

    i = 0
    result = 0
    while ((i * shift) < 32):
        partmask = int('0' * (32 - shift) + '1' * shift, base = 2) << (shift * i)
        part = value & partmask
        value ^= (part << shift) & mask
        result |= part
        i += 1
    return result

def rand_to_state(value: int):
    """
    - input : `value (int)`
    - output : `value (int)` , for MT19937
    """

    value = un_bitshift_right_xor(value, 18)
    value = un_bitshift_left_xor_mask(value, 15, 0xefc60000)
    value = un_bitshift_left_xor_mask(value, 7, 0x9d2c5680)
    value = un_bitshift_right_xor(value, 11)
    return value

def state_to_rand(value: int):
    """
    - input : `value (int)`
    - output : `value (int)` , for MT19937
    """

    value ^= (value >> 11)
    value ^= (value << 7) & 0x9d2c5680
    value ^= (value << 15) & 0xefc60000
    value ^= (value >> 18)
    return value

def gen_next_state(state: list[int]):
        """
        - input : `state (list[int])` , `state` will be changed to next state
        - output : None
        """

        assert len(state) == 624
        for i in range(624):
            y = (state[i] & 0x80000000) + (state[(i + 1) % 624] & 0x7fffffff)
            next = y >> 1
            next ^= state[(i + 397) % 624]
            if ((y & 1) == 1):
                next ^= 0x9908b0df
            state[i] = next


from pwn import *
from tqdm import trange

r = remote('127.0.0.1', 30003)
r.recvline()

def get_random():
    r.sendlineafter(b'> ', b'-1')
    return int(r.recvline().strip().split(b'is ')[1].decode()) - 0x80000000

randlist = [get_random() for _ in trange(624 * 2)]

state = [rand_to_state(randlist[0] << 1)]
for i in range(624):
    s_test = rand_to_state(randlist[i + 1] << 1)
    s_xor = rand_to_state(randlist[i + 397] << 1)
    s_new = rand_to_state(randlist[i + 624] << 1)

    if (bin((s_test >> 1) ^ s_xor)[2:].rjust(32, '0')[11] != bin(s_new)[2:].rjust(32, '0')[11]):
        state.append(rand_to_state((randlist[i + 1] << 1) | 1))
    else:
        state.append(s_test)

state, next_state0 = state[:-1] ,state[-1]
gen_next_state(state)
state[0] = next_state0

gen_next_state(state)

for i in range(100):
    r.sendlineafter(b'> ', str((state_to_rand(state[i]) >> 1) + 0x80000000).encode())
    r.recvline()

r.interactive()