import re
c = open('build_repo.py','r',encoding='utf-8').read()
# Find the Dockerfile w() call line and replace it
pattern = r"w\('Dockerfile'[^\n]*\n"
replacement = """dockerfile_content = "FROM python:3.11-slim\\n\\nWORKDIR /app\\n\\nCOPY requirements.txt .\\nRUN pip install --no-cache-dir -r requirements.txt\\n\\nCOPY app/ ./app/\\n\\nEXPOSE 8000\\n\\nCMD [\\"uvicorn\\", \\"app.main:app\\", \\"--host\\", \\"0.0.0.0\\", \\"--port\\", \\"8000\\"]\\n"
w('Dockerfile', dockerfile_content)
"""
c = re.sub(pattern, replacement, c, count=1)
open('build_repo.py','w',encoding='utf-8').write(c)
print('Fixed')