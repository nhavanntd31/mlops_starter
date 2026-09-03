c = open('build_repo.py','r',encoding='utf-8').read()
lines = c.split('\n')
for i in range(1005, min(1020, len(lines))):
    # check for backslash issues
    if '\\U' in lines[i] or '\\u' in lines[i]:
        print(f'ISSUE at {i}: {repr(lines[i][:120])}')
    else:
        print(f'{i}: {lines[i][:100]}')