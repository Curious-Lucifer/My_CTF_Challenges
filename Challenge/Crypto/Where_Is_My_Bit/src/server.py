import random, sys
from secret import FLAG

print('Can you find my bit ?')

count = 0
while count < 100:
    try:
        ans = random.randrange(0x80000000, 0xFFFFFFFF)
        num = int(input('> '))
        if num == ans:
            print(f'Lucky you !')
            count += 1
        else:
            print(f'Wrong, answer is {ans}')
            count = 0
    except:
        sys.exit()

print(f'flag : {FLAG}')