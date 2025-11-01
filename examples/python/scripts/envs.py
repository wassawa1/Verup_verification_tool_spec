#!/usr/bin/env python3
"""
Environment preparation and setup script
- Loads settings from settings.json
- Sets up Python environments using uv
- Outputs environment variables as key=value lines
"""
import os
import sys
import json
import subprocess


def install_uv():
    """uvを自動インストール (Ubuntu/Linux想定)"""
    print("[envs] Installing uv...", file=sys.stderr)
    
    install_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
    result = subprocess.run(install_cmd, shell=True)
    
    if result.returncode != 0:
        print("[envs] ❌ Failed to install uv", file=sys.stderr)
        sys.exit(1)
    
    # uvのPATHを追加 (~/.local/bin)
    uv_bin = os.path.expanduser("~/.local/bin")
    if uv_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{uv_bin}:{os.environ.get('PATH', '')}"
    
    print("[envs] ✅ uv installed", file=sys.stderr)


def setup_python_with_uv(version):
    """uvを使ってPython環境をセットアップ"""
    print(f"[envs] Setting up Python {version}...", file=sys.stderr)
    
    result = subprocess.run(
        ["uv", "python", "install", version],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 or "already installed" in result.stderr.lower() or "already installed" in result.stdout.lower():
        print(f"[envs] ✅ Python {version} ready", file=sys.stderr)
    else:
        print(f"[envs] ⚠️  Python {version} setup issue: {result.stderr}", file=sys.stderr)

# settings.json から設定を読み込む
settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
with open(settings_path, "r", encoding="utf-8") as f:
    settings = json.load(f)

project = settings["project"]
old_version = settings["old_version"]
new_version = settings["new_version"]

# Python実行コマンドを生成
python_old = f"uv run --python {old_version} python"
python_new = f"uv run --python {new_version} python"

directories = settings.get("directories", {
    "testcases": "testcases",
    "sim_new": "sim_new",
    "sim_old": "sim_old",
    "tmp": "tmp",
    "reports": "reports"
})

# uv環境のセットアップ
try:
    subprocess.run(["uv", "--version"], capture_output=True, check=True)
except (FileNotFoundError, subprocess.CalledProcessError):
    install_uv()

# Pythonバージョンをインストール
setup_python_with_uv(old_version)
setup_python_with_uv(new_version)

print(f"project={project}")
print(f"old_version={old_version}")
print(f"new_version={new_version}")
print(f"python_old={python_old}")
print(f"python_new={python_new}")

# Export directory paths for downstream scripts
for key, value in directories.items():
    print(f"DIR_{key.upper()}={value}")
