"""
Check Kaggle kernel execution status.
"""
import os
import subprocess

os.environ['KAGGLE_API_TOKEN'] = 'KGAT_a2d6319e4d194ff2bc616246b32b5e8c'

res = subprocess.run(['py', '-3.12', '-m', 'kaggle', 'kernels', 'status', 'harsimarsingh23/arc-prize-2026-arc-agi-3-starter'], capture_output=True, text=True, env=os.environ)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
print("RETURNCODE:", res.returncode)
