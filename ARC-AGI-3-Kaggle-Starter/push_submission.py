import os
import sys
import subprocess

os.environ['KAGGLE_API_TOKEN'] = 'KGAT_a2d6319e4d194ff2bc616246b32b5e8c'

print("Pushing notebook to Kaggle...")
res = subprocess.run(['py', '-3.12', '-m', 'kaggle', 'kernels', 'push', '-p', 'notebooks/'], capture_output=True, text=True, env=os.environ)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
print("RETURNCODE:", res.returncode)
