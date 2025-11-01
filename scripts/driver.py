import os
import sys
import subprocess
import time
import psutil
from pathlib import Path

def get_testcases():
    testcase_dir = Path('testcases')
    return sorted([f.name for f in testcase_dir.glob('*.py')])

def run_testcase(testcase_name, testcase_file, sim_dir, python_cmd):
    """テストケースを実行してメトリクスを収集"""
    start_time = time.time()
    
    # プロセスを起動してメモリ使用量を監視
    process = subprocess.Popen(
        [python_cmd, testcase_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    # メモリ使用量の最大値を追跡
    max_memory_kb = 0
    try:
        ps_process = psutil.Process(process.pid)
        while process.poll() is None:
            try:
                mem_info = ps_process.memory_info()
                memory_kb = mem_info.rss // 1024  # bytes to KB
                max_memory_kb = max(max_memory_kb, memory_kb)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            time.sleep(0.01)  # 10ms間隔でサンプリング
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        # プロセスが既に終了している場合
        pass
    
    stdout, stderr = process.communicate()
    elapsed = int((time.time() - start_time) * 1000)
    errors = 1 if process.returncode != 0 else 0
    
    return {
        'latency': elapsed,
        'errors': errors,
        'memory_kb': max_memory_kb,
        'stdout': stdout,
        'stderr': stderr
    }

version = os.environ.get('RUN_VERSION', 'new')
sim_dir = 'sim_old' if version == 'old' else 'sim_new'
os.makedirs(sim_dir, exist_ok=True)

# Select Python version based on RUN_VERSION
# Users can customize these paths for their environment
if version == 'old':
    # Old version: Python 3.9 (example)
    python_cmd = os.environ.get('PYTHON_OLD', 'python3.9')
else:
    # New version: Python 3.11 (example)
    python_cmd = os.environ.get('PYTHON_NEW', 'python3.11')

# Fallback to current Python if specific version not found
try:
    result = subprocess.run([python_cmd, '--version'], capture_output=True, timeout=5)
    if result.returncode != 0:
        python_cmd = sys.executable
        print(f'Warning: Specified Python not found, using {python_cmd}', file=sys.stderr)
except (FileNotFoundError, subprocess.TimeoutExpired):
    python_cmd = sys.executable
    print(f'Warning: {python_cmd} not available, using current Python: {sys.executable}', file=sys.stderr)

testcases = get_testcases()
if not testcases:
    print('Error: No testcases found', file=sys.stderr)
    sys.exit(1)

print(f'[driver] Processing {len(testcases)} testcases', file=sys.stderr)

total_latency = 0
total_errors = 0
total_memory = 0
aggregated_lines = []

for tc in testcases:
    name = Path(tc).stem
    print(f'  {name}...', file=sys.stderr)
    result = run_testcase(name, f'testcases/{tc}', sim_dir, python_cmd)
    total_latency += result['latency']
    total_errors += result['errors']
    total_memory += result['memory_kb']
    
    # Write individual log
    with open(f'{sim_dir}/{name}.log', 'w') as f:
        f.write(f'=== Testcase: {name} ===\n')
        f.write(f'Latency: {result["latency"]} ms\n')
        f.write(f'Errors: {result["errors"]}\n')
        f.write(f'Memory: {result["memory_kb"]} KB\n')
        f.write(f'\n{result["stdout"]}\n')
    
    # Collect for aggregated log
    latency_sec = result['latency'] / 1000.0
    aggregated_lines.append(f'{name}: {latency_sec:.3f}s, {result["errors"]} errors, {result["memory_kb"]} KB')

# Write aggregated log for metric_framework.py
with open(f'{sim_dir}/aggregated.log', 'w') as f:
    f.write('\n'.join(aggregated_lines))

print(f'latency_ms={total_latency}')
print(f'error_count={total_errors}')
print(f'memory_kb={total_memory}')
print(f'testcases_count={len(testcases)}')
