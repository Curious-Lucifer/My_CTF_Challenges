from secret import FLAG

print("Who published https://www.youtube.com/watch?v=dQw4w9WgXcQ ?")

if input('> ') == 'Rick Astley':
    print(f'Flag : {FLAG}', flush=True)
else:
    print('???', flush=True)
