#!/usr/bin/env python3
"""
バリデーションユーティリティ: プロジェクト設定をチェック

使い方:
  python scripts/validate.py
"""
import os
import sys
import json
from pathlib import Path

def print_status(check_name, passed, message=""):
    """Print validation status"""
    icon = "✅" if passed else "❌"
    print(f"{icon} {check_name}")
    if message:
        indent = "   "
        print(f"{indent}💡 {message}")
    return passed

def validate_settings():
    """Validate settings.json"""
    print("\n📋 Checking settings.json...")
    settings_path = Path("scripts/settings.json")
    
    if not settings_path.exists():
        print_status("settings.json exists", False, "Run: cp scripts/settings.json.example scripts/settings.json")
        return False
    
    print_status("settings.json exists", True)
    
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        print_status("settings.json is valid JSON", True)
    except json.JSONDecodeError as e:
        print_status("settings.json is valid JSON", False, f"JSON error: {e}")
        return False
    
    # Check required fields
    required_fields = ["project", "old_version", "new_version"]
    all_present = True
    for field in required_fields:
        present = field in settings
        print_status(f"  '{field}' field", present)
        all_present = all_present and present
    
    # Check simulation tool
    tool = settings.get("simulation_tool", "iverilog")
    print(f"   🔧 Simulation tool: {tool}")
    
    return all_present

def validate_testcases():
    """Validate testcases directory"""
    print("\n📁 Checking testcases...")
    
    # Load settings to get directory configuration
    settings_path = Path("scripts/settings.json")
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        testcases_dir = settings.get("directories", {}).get("testcases", "testcases")
    else:
        testcases_dir = "testcases"
    
    testcase_dir = Path(testcases_dir)
    
    if not testcase_dir.exists():
        print_status(f"{testcases_dir}/ directory exists", False, f"Create: mkdir {testcases_dir}")
        return False
    
    print_status(f"{testcases_dir}/ directory exists", True)
    
    testcases = list(testcase_dir.glob("*.v"))
    if not testcases:
        print_status("Has .v files", False, f"Add Verilog test files to {testcases_dir}/")
        return False
    
    print_status(f"Has {len(testcases)} .v files", True)
    for tc in testcases[:5]:  # Show first 5
        print(f"     - {tc.name}")
    if len(testcases) > 5:
        print(f"     ... and {len(testcases) - 5} more")
    
    return True

def validate_directories():
    """Validate required directories"""
    print("\n📂 Checking directories...")
    
    # Load settings to get directory configuration
    settings_path = Path("scripts/settings.json")
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        directories = settings.get("directories", {
            "testcases": "testcases",
            "sim_new": "sim_new",
            "sim_old": "sim_old",
            "tmp": "tmp",
            "reports": "reports"
        })
    else:
        directories = {
            "testcases": "testcases",
            "sim_new": "sim_new",
            "sim_old": "sim_old",
            "tmp": "tmp",
            "reports": "reports"
        }
    
    dirs_to_check = [
        ("scripts/", "Core scripts directory", False),
        ("tools/", "Framework tools directory", False),
        (f"{directories['reports']}/", "Report output directory", True),
        (f"{directories['tmp']}/", "Temporary files directory", True),
    ]
    
    all_ok = True
    for dir_path, description, auto_created in dirs_to_check:
        exists = Path(dir_path).exists()
        
        if not exists and not auto_created:
            print_status(f"{dir_path}", False, f"Create: mkdir {dir_path}")
            all_ok = False
        else:
            status_msg = f"{description} (auto-created)" if auto_created else description
            print_status(f"{dir_path}", True, status_msg)
    
    return all_ok

def validate_tools():
    """Check if simulation tool is available"""
    print("\n🔧 Checking simulation tools...")
    
    settings_path = Path("scripts/settings.json")
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        tool = settings.get("simulation_tool", "iverilog")
    else:
        tool = "iverilog"
    
    print(f"   Selected tool: {tool}")
    
    # Check if tool is in PATH
    import shutil
    tool_cmd = {
        "iverilog": "iverilog",
        "vivado": "xvlog",
        "modelsim": "vlog",
    }.get(tool, tool)
    
    tool_path = shutil.which(tool_cmd)
    if tool_path:
        print_status(f"{tool_cmd} is available", True, f"Found at: {tool_path}")
        return True
    else:
        print_status(f"{tool_cmd} is available", False, 
                    f"Install {tool} or add to PATH, or set dry_run: true in settings.json")
        return False

def main():
    print("=" * 60)
    print("🔍 Project Validation")
    print("=" * 60)
    
    results = []
    results.append(validate_settings())
    results.append(validate_testcases())
    results.append(validate_directories())
    results.append(validate_tools())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed! Ready to run pipeline.")
        print("\nNext steps:")
        print("  1. Review settings.json")
        print("  2. Run: python run_pipeline.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  - Missing settings.json: Check scripts/ directory")
        print("  - No testcases: Add .v files to testcases/")
        print("  - Tool not found: Set 'dry_run': true in settings.json for testing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
