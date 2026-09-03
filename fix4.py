c = open('build_repo.py','r',encoding='utf-8').read()
lines = c.split('\n')
# Line 488 has the proper dockerfile_content = "..."
# Lines 489-502 are leftovers that need to be removed
# Keep line 488 (dockerfile_content) and line 501 (w('Dockerfile'...))
# Remove lines 489-500 and line 502
new_lines = lines[:489] + [lines[501]] + lines[503:]
open('build_repo.py','w',encoding='utf-8').write('\n'.join(new_lines))
print('Cleaned up. Verifying...')
c2 = open('build_repo.py','r',encoding='utf-8').read()
lines2 = c2.split('\n')
for i in range(486, min(496, len(lines2))):
    print(f'{i}: {lines2[i][:100]}')