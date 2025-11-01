#!/usr/bin/env python3
"""
Test execution driver for Python verification
- Executes test cases using specified Python versions (via uv)
- Monitors execution time and memory usage
- Aggregates results and outputs metrics
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# uvのPATHを追加 (Ubuntu/Linux環境)
uv_bin = os.path.expanduser("~/.local/bin")
if uv_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{uv_bin}:{os.environ.get('PATH', '')}"

# psutilのインポートは任意（なければメモリ測定をスキップ）
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available, memory measurement will be skipped", file=sys.stderr)

def get_testcases():
    testcase_dir = Path('testcases')
    return sorted([f.name for f in testcase_dir.glob('*.py')])

def run_testcase(testcase_name, testcase_file, sim_dir, python_cmd_list):
    """テストケースを実行してメトリクスを収集
    
    Args:
        python_cmd_list: Python実行コマンドのリスト (例: ['python3.9'] or ['uv', 'run', '--python', '3.9', 'python'])
    """
    start_time = time.time()
    
    # プロセスを起動してメモリ使用量を監視
    process = subprocess.Popen(
        python_cmd_list + [testcase_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    # メモリ使用量の最大値を追跡
    max_memory_kb = 0
    if PSUTIL_AVAILABLE:
        try:
            ps_process = psutil.Process(process.pid)
            # 最初のメモリ測定
            try:
                mem_info = ps_process.memory_info()
                max_memory_kb = mem_info.rss // 1024
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            # プロセスが実行中の間、継続的に測定
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
    else:
        # psutilが利用できない場合は完了を待つだけ
        process.wait()
    
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
# Users can customize these paths in settings.json or via environment variables
if version == 'old':
    # Old version: from PYTHON_OLD env var or settings.json
    python_cmd = os.environ.get('PYTHON_OLD') or os.environ.get('python_old')
    if not python_cmd:
        print(f'Error: PYTHON_OLD or python_old not specified for old version', file=sys.stderr)
        print(f'Please set python_old in settings.json or PYTHON_OLD environment variable', file=sys.stderr)
        sys.exit(1)
else:
    # New version: from PYTHON_NEW env var or settings.json
    python_cmd = os.environ.get('PYTHON_NEW') or os.environ.get('python_new')
    if not python_cmd:
        print(f'Error: PYTHON_NEW or python_new not specified for new version', file=sys.stderr)
        print(f'Please set python_new in settings.json or PYTHON_NEW environment variable', file=sys.stderr)
        sys.exit(1)

# Parse command (could be "python3.9" or "uv run --python 3.9 python")
python_cmd_list = python_cmd.split()

# Verify Python is available and get version
try:
    version_cmd = python_cmd_list + ['--version']
    result = subprocess.run(version_cmd, capture_output=True, timeout=5, text=True)
    if result.returncode == 0:
        actual_version = result.stdout.strip() or result.stderr.strip()
        print(f'Using Python: {python_cmd} ({actual_version})', file=sys.stderr)
        
        # Export version for reporting (format: "Python 3.11.5" -> "Python 3.11")
        if version == 'old':
            print(f'old_version={actual_version}')
        else:
            print(f'new_version={actual_version}')
    else:
        print(f'Error: Python command "{python_cmd}" failed to execute', file=sys.stderr)
        sys.exit(1)
except (FileNotFoundError, subprocess.TimeoutExpired):
    print(f'Error: Python command "{python_cmd}" not found or timed out', file=sys.stderr)
    sys.exit(1)

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
    result = run_testcase(name, f'testcases/{tc}', sim_dir, python_cmd_list)
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
