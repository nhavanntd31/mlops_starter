c = open('build_repo.py','r',encoding='utf-8').read()
# Find line 489 area
lines = c.split('\n')
# Find the dockerfile_content line
for i, line in enumerate(lines):
    if 'dockerfile_content' in line and 'FROM' in line:
        # Replace this line and next line with proper single-line version
        lines[i] = 'dockerfile_content = "FROM python:3.11-slim\\n\\nWORKDIR /app\\n\\nCOPY requirements.txt .\\nRUN pip install --no-cache-dir -r requirements.txt\\n\\nCOPY app/ ./app/\\n\\nEXPOSE 8000\\n\\nCMD [\\"uvicorn\\", \\"app.main:app\\", \\"--host\\", \\"0.0.0.0\\", \\"--port\\", \\"8000\\"]\\n"'
        # Check if next line is the w('Dockerfile') call
        if i+1 < len(lines) and "w('Dockerfile'" in lines[i+1]:
            pass  # keep it
        print(f'Fixed line {i}: {lines[i][:80]}')
        break
open('build_repo.py','w',encoding='utf-8').write('\n'.join(lines))
print('Done')