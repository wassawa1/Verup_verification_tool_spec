#!/usr/bin/env python3
"""
Complete verification pipeline runner
Stages 1-4 executed in sequence with environment variable inheritance
"""
import subprocess
import sys
import os
import shutil
import json
from pathlib import Path

# Set UTF-8 encoding for stdout/stderr on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def load_settings():
    """Load settings from scripts/settings.json"""
    settings_path = Path("scripts/settings.json")
    if not settings_path.exists():
        print("⚠️  Warning: settings.json not found, using defaults", file=sys.stderr)
        return {
            "directories": {
                "testcases": "testcases",
                "sim_new": "sim_new",
                "sim_old": "sim_old",
                "tmp": "tmp",
                "reports": "reports",
                "logs": "logs"
            }
        }
    
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()
        # Remove // style comments
        lines = []
        for line in content.split('\n'):
            if '//' in line:
                before_comment = line.split('//')[0]
                lines.append(before_comment)
            else:
                lines.append(line)
        return json.loads('\n'.join(lines))


def run_stage(stage_num, script, env_vars=None, directories=None):
    """Run a pipeline stage"""
    full_env = os.environ.copy()
    if env_vars:
        full_env.update(env_vars)
    
    print(f"\n{'='*60}")
    print(f"[Stage {stage_num}] {script}")
    print(f"{'='*60}")
    
    try:
        # Capture output to file
        tmp_dir = directories.get("tmp", "tmp") if directories else "tmp"
        output_file = f"{tmp_dir}/stage{stage_num}_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            result = subprocess.run(
                [sys.executable, script],
                env=full_env,
                stdout=f,
                stderr=subprocess.STDOUT,
                timeout=300
            )
        
        # Display captured output
        with open(output_file, "r", encoding="utf-8", errors='replace') as f:
            output = f.read()
            print(output)
        
        if result.returncode != 0:
            print(f"❌ Stage {stage_num} failed with exit code {result.returncode}", file=sys.stderr)
            return False
        
        return True
    except subprocess.TimeoutExpired:
        print(f"❌ Stage {stage_num} timed out")
        return False
    except Exception as e:
        print(f"❌ Stage {stage_num} failed: {e}")
        return False


def parse_stage_output(filename):
    """Parse key=value output from stage"""
    data = {}
    try:
        with open(filename, "r", encoding="utf-8", errors='replace') as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    data[key.strip()] = value.strip()
    except Exception as e:
        print(f"Warning: Failed to parse {filename}: {e}", file=sys.stderr)
    return data


def main():
    # Load settings
    settings = load_settings()
    directories = settings.get("directories", {
        "testcases": "testcases",
        "sim_new": "sim_new",
        "sim_old": "sim_old",
        "tmp": "tmp",
        "reports": "reports",
        "logs": "logs"
    })
    
    # Clean up previous execution results
    print("Cleaning up previous execution results...")
    for key in ["sim_new", "sim_old", "tmp"]:
        dir_path = directories[key]
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    
    # Create necessary directories
    for key in directories:
        os.makedirs(directories[key], exist_ok=True)
    
    print("\n" + "="*60)
    print("  Version Upgrade Verification Pipeline")
    print("  (Local Test)")
    print("="*60)
    
    # Stage 1: Environment Setup
    print("\n[Stage 1] Environment Setup\n")
    if not run_stage(1, "scripts/envs.py", directories=directories):
        sys.exit(1)
    
    # Read environment setup output
    tmp_dir = directories.get("tmp", "tmp")
    stage1_output = parse_stage_output(f"{tmp_dir}/stage1_output.txt")
    
    # Get environment variables from stage1 (envs.py) with fallbacks
    env_vars = {
        "PROJECT": stage1_output.get("project", os.environ.get("PROJECT", "design_verification")),
        "OLD_VERSION": stage1_output.get("old_version", os.environ.get("OLD_VERSION", "v1.0")),
        "NEW_VERSION": stage1_output.get("new_version", os.environ.get("NEW_VERSION", "v2.0")),
        # Thresholds are now dynamically defined in monitor.py
    }
    
    tmp_dir = directories["tmp"]
    stage1_output = parse_stage_output(f"{tmp_dir}/stage1_output.txt")
    env_vars.update(stage1_output)
    
    # Stage 2: Verification Execution (Old Version)
    print("\n[Stage 2a] Verification Execution (OLD_VERSION)\n")
    env_vars["RUN_VERSION"] = "old"
    if not run_stage(2, "scripts/driver.py", env_vars, directories):
        sys.exit(1)
    
    # Stage 2: Verification Execution (New Version)
    print("\n[Stage 2b] Verification Execution (NEW_VERSION)\n")
    env_vars["RUN_VERSION"] = "new"
    if not run_stage(2, "scripts/driver.py", env_vars, directories):
        sys.exit(1)
    
    stage2_output = parse_stage_output(f"{tmp_dir}/stage2_output.txt")
    env_vars.update(stage2_output)
    
    print(f"\nStage 2 output: {stage2_output}\n")
    
    # Set paths for old and new logs before Stage 3
    sim_new = directories["sim_new"]
    sim_old = directories["sim_old"]
    env_vars["NEW_LOG_PATH"] = f"{sim_new}/aggregated.log"
    env_vars["OLD_LOG_PATH"] = f"{sim_old}/aggregated.log"
    
    # Stage 3: Metrics Extraction
    print("\n[Stage 3] Metrics Extraction\n")
    if not run_stage(3, "scripts/monitor.py", env_vars, directories):
        sys.exit(1)
    
    stage3_output = parse_stage_output(f"{tmp_dir}/stage3_output.txt")
    env_vars.update(stage3_output)
    
    print(f"\nStage 3 output: {stage3_output}\n")
    
    # Extract old version metrics separately
    print("Extracting old version metrics...")
    # OLD_LOG_PATH already set above
    old_env = env_vars.copy()
    old_env["NEW_LOG_PATH"] = f"{sim_old}/aggregated.log"
    
    # Run monitor again to get old version metrics
    old_env = env_vars.copy()
    old_env["NEW_LOG_PATH"] = f"{sim_old}/aggregated.log"
    try:
        old_output_file = f"{tmp_dir}/stage3_old_output.txt"
        with open(old_output_file, "w", encoding="utf-8") as f:
            result = subprocess.run(
                ["python3", "scripts/monitor.py"],
                env={**os.environ, **old_env},
                stdout=f,
                stderr=subprocess.STDOUT,
                timeout=300
            )
        
        old_stage3_output = parse_stage_output(old_output_file)
        
        # Prefix ALL old metrics with "OLD_" (don't filter, take everything from monitor.py)
        for key, value in old_stage3_output.items():
            env_vars[f"OLD_{key.upper()}"] = value
        
        print(f"Old version metrics: {old_stage3_output}\n")
    except Exception as e:
        print(f"Warning: Could not extract old version metrics: {e}\n")
    
    # Stage 4: Validation & Reporting
    print("\n[Stage 4] Validation & Reporting")
    print("="*60)
    
    print("\nFinal environment variables for Stage 4:")
    for key in sorted(env_vars.keys()):
        if env_vars[key] not in ["", "N/A", "None"]:
            print(f"  {key}={env_vars[key]}")
    
    print("\nRunning validation script (scoreboard)...")
    if not run_stage(4, "scripts/scoreboard.py", env_vars, directories):
        print("Validation failed")
    else:
        print("Validation result: PASSED")
    
    print("\nGenerating verification report...")
    
    # Write env_vars to a temp file to preserve them
    env_file = f"{tmp_dir}/stage4_env.txt"
    with open(env_file, "w", encoding="utf-8") as f:
        for key, value in sorted(env_vars.items()):
            f.write(f"{key}={value}\n")
    
    # Set the environment file location for export_report.py to read
    full_env = os.environ.copy()
    full_env.update(env_vars)
    full_env["STAGE4_ENV_FILE"] = os.path.abspath(env_file)
    
    result = subprocess.run(
        [sys.executable, "tools/export_report.py"],
        env=full_env,
        capture_output=False,
        text=True
    )
    
    # Summary
    print("\n" + "="*60)
    print("  Pipeline Completed")
    print("="*60)
    
    # Find latest report
    reports_dir = Path("reports")
    if reports_dir.exists():
        reports = sorted(reports_dir.glob("report-*.md"), reverse=True)
        if reports:
            latest = reports[0]
            print(f"\nLatest report: {latest}")
            print(f"Open in VS Code to view: code {latest}")
            print("\nReport summary:")
            print(f"  - Project: {env_vars.get('PROJECT', 'N/A')}")
            print(f"  - Versions: {env_vars.get('OLD_VERSION', 'N/A')} vs {env_vars.get('NEW_VERSION', 'N/A')}")
            print("  - Status: PASSED" if result.returncode == 0 else "  - Status: FAILED")


if __name__ == "__main__":
    main()
