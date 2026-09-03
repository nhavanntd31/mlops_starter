c = open('build_repo.py','r',encoding='utf-8').read()
# The ps1 content has \u escapes that Python interprets inside triple-quoted strings
# We need to find the w('scripts/run_e2e_demo.ps1' call and make it use raw strings or pre-decoded text
# Actually the issue is the \U and \u inside triple quotes being parsed as unicode escapes
# Solution: the Vietnamese text in ps1 content should use actual unicode chars, not \u escapes

# Find all \uXXXX patterns in triple-quoted strings and decode them
import re
def decode_unicode_escapes(text):
    def replacer(m):
        try:
            return chr(int(m.group(1), 16))
        except:
            return m.group(0)
    return re.sub(r'\\u([0-9a-fA-F]{4})', replacer, text)

c = decode_unicode_escapes(c)
open('build_repo.py','w',encoding='utf-8').write(c)
print('Fixed unicode escapes')
# Verify no more \u patterns
remaining = re.findall(r'\\u[0-9a-fA-F]{4}', c)
print(f'Remaining \\u patterns: {len(remaining)}')