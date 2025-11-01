#!/usr/bin/env python3
"""
Driver: Execute all testcases and aggregate metrics into single report
Supports both OLD_VERSION and NEW_VERSION execution via RUN_VERSION env var

🔧 カスタマイズガイド:
  1. settings.json で simulation_tool を選択 (iverilog/vivado/modelsim)
  2. カスタムツールの場合は run_simulation() を編集
  3. debug_mode: true で詳細ログ出力
  4. dry_run: true でコマンドを実行せずプリント
"""
import os
import subprocess
import sys
import time
import json
from pathlib import Path

def load_settings():
    """Load settings from settings.json"""
    settings_path = Path(__file__).parent / "settings.json"
    if not settings_path.exists():
        print("⚠️  Warning: settings.json not found, using defaults", file=sys.stderr)
        return {}
    
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)

def debug_print(message, settings):
    """Print debug message if debug_mode is enabled"""
    if settings.get("debug_mode", False):
        print(f"🐛 [DEBUG] {message}", file=sys.stderr)

def get_testcases(settings):
    """Get all .v files from testcases directory"""
    testcases_dir = settings.get("directories", {}).get("testcases", "testcases")
    testcase_dir = Path(testcases_dir)
    testcases = sorted([f.name for f in testcase_dir.glob("*.v")])
    return testcases

def run_simulation(testcase_name, verilog_code, sim_dir):
    """Run single testcase simulation
    
    🔧 カスタマイズポイント:
      - settings.json の simulation_tool を変更
      - または、このメソッドを直接編集してカスタムツールに対応
    """
    settings = load_settings()
    tool = settings.get("simulation_tool", "iverilog")
    debug_mode = settings.get("debug_mode", False)
    dry_run = settings.get("dry_run", False)
    
    start_time = time.time()
    
    testcase_file = f"{sim_dir}/{testcase_name}.v"
    with open(testcase_file, "w") as f:
        f.write(verilog_code)
    
    debug_print(f"Processing {testcase_name} with {tool}", settings)
    
    # ========================================
    # ツール別実装（settings.json で選択）
    # ========================================
    
    if tool == "iverilog":
        # Icarus Verilog
        compile_cmd = ["iverilog", "-o", f"{testcase_name}.vvp", f"{testcase_name}.v"]
        simulate_cmd = ["vvp", f"{testcase_name}.vvp"]
        
    elif tool == "vivado":
        # Xilinx Vivado
        compile_cmd = ["xvlog", f"{testcase_name}.v"]
        simulate_cmd = ["xsim", testcase_name, "-R"]
        
    elif tool == "modelsim":
        # Mentor ModelSim
        compile_cmd = ["vlog", f"{testcase_name}.v"]
        simulate_cmd = ["vsim", "-c", f"work.{testcase_name}", "-do", "run -all; quit"]
        
    else:
        # ========================================
        # カスタムツール実装例
        # ========================================
        # compile_cmd = ["your-tool", "compile", f"{testcase_name}.v"]
        # simulate_cmd = ["your-tool", "simulate", testcase_name]
        print(f"❌ Error: Unknown simulation_tool '{tool}'", file=sys.stderr)
        print(f"💡 Hint: Edit settings.json or implement custom tool in driver.py", file=sys.stderr)
        sys.exit(1)
    
    # Dry run mode: コマンドをプリントのみ
    if dry_run:
        print(f"[DRY RUN] Compile: {' '.join(compile_cmd)}", file=sys.stderr)
        print(f"[DRY RUN] Simulate: {' '.join(simulate_cmd)}", file=sys.stderr)
        return {
            "latency": 0.0,
            "errors": 0,
            "stdout": "[dry run mode]",
            "stderr": ""
        }
    
    # Compile
    debug_print(f"Compile: {' '.join(compile_cmd)}", settings)
    compile_result = subprocess.run(
        compile_cmd,
        capture_output=True,
        text=True,
        cwd=sim_dir
    )
    
    if debug_mode and compile_result.stderr:
        print(f"🐛 Compile stderr:\n{compile_result.stderr}", file=sys.stderr)
    
    # Simulate
    debug_print(f"Simulate: {' '.join(simulate_cmd)}", settings)
    sim_result = subprocess.run(
        simulate_cmd,
        capture_output=True,
        text=True,
        cwd=sim_dir
    )
    
    if debug_mode and sim_result.stderr:
        print(f"🐛 Simulate stderr:\n{sim_result.stderr}", file=sys.stderr)
    
    latency = time.time() - start_time
    all_stderr = compile_result.stderr + sim_result.stderr
    error_count = len([l for l in all_stderr.split('\n') if l and 'error' in l.lower()])
    
    debug_print(f"Completed in {latency:.3f}s with {error_count} errors", settings)
    
    return {
        "latency": latency,
        "errors": error_count,
        "stdout": sim_result.stdout,
        "stderr": all_stderr
    }

def main():
    # Load settings
    settings = load_settings()
    debug_mode = settings.get("debug_mode", False)
    directories = settings.get("directories", {
        "testcases": "testcases",
        "sim_new": "sim_new",
        "sim_old": "sim_old",
        "tmp": "tmp",
        "reports": "reports"
    })
    
    # Determine which version to run (old or new)
    version = os.environ.get("RUN_VERSION", "new")  # "old" or "new"
    sim_dir = directories["sim_old"] if version == "old" else directories["sim_new"]
    
    os.makedirs(directories["sim_old"], exist_ok=True)
    os.makedirs(directories["sim_new"], exist_ok=True)
    
    testcases = get_testcases(settings)
    if not testcases:
        print(f"❌ Error: No testcases found in {directories['testcases']}/ directory", file=sys.stderr)
        print(f"💡 Hint: Add .v files to {directories['testcases']}/ directory", file=sys.stderr)
        sys.exit(1)
    
    print(f"[driver] Processing {len(testcases)} testcases with {settings.get('simulation_tool', 'iverilog')}", file=sys.stderr)
    if settings.get("dry_run", False):
        print("⚠️  DRY RUN MODE: Commands will be printed but not executed", file=sys.stderr)
    
    total_latency = 0.0
    total_errors = 0
    results = []
    
    testcases_dir = directories["testcases"]
    # Process each testcase
    for testcase in testcases:
        testcase_name = Path(testcase).stem
        with open(f"{testcases_dir}/{testcase}", "r") as f:
            code = f.read()
        
        print(f"  {testcase_name}...", file=sys.stderr)
        
        # Run simulation in appropriate directory
        try:
            result = run_simulation(testcase_name, code, sim_dir)
            total_latency += result["latency"]
            total_errors += result["errors"]
            results.append({
                "name": testcase_name,
                "latency": result["latency"],
                "errors": result["errors"]
            })
        except Exception as e:
            print(f"❌ Error processing {testcase_name}: {e}", file=sys.stderr)
            if debug_mode:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    # Write aggregated results
    with open(f"{sim_dir}/aggregated.log", "w") as f:
        f.write(f"Total testcases: {len(results)}\n")
        f.write(f"Total latency: {total_latency:.3f}s\n")
        f.write(f"Total errors: {total_errors}\n\n")
        for r in results:
            f.write(f"{r['name']}: {r['latency']:.3f}s, {r['errors']} errors\n")
    
    # Set environment variables
    latency = os.environ.get("SIM_LATENCY", str(total_latency * 1000))
    errors = os.environ.get("SIM_ERRORS", str(total_errors))
    
    print(f"latency={latency}")
    print(f"errors={errors}")
    print(f"testcases_count={len(results)}")

if __name__ == "__main__":
    main()
