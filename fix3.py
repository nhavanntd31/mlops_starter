c = open('build_repo.py','r',encoding='utf-8').read()
lines = c.split('\n')
# Print lines around 488-500
for i in range(485, min(505, len(lines))):
    print(f'{i}: {lines[i][:100]}')