#!/usr/bin/env python3
"""
Environment preparation script for Verilog verification
- Loads settings from settings.json
- Creates necessary directories
- Outputs environment variables as key=value lines
"""
import os
import json

# settings.json から設定を読み込む
settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
if os.path.exists(settings_path):
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)
    
    # settings.jsonから必須項目を取得（デフォルト値なし）
    if "project" not in settings:
        raise ValueError("settings.json に 'project' キーが必要です")
    if "old_version" not in settings:
        raise ValueError("settings.json に 'old_version' キーが必要です")
    if "new_version" not in settings:
        raise ValueError("settings.json に 'new_version' キーが必要です")
    
    project = settings["project"]
    old_version = settings["old_version"]
    new_version = settings["new_version"]
    directories = settings.get("directories", {
        "testcases": "testcases",
        "sim_new": "sim_new",
        "sim_old": "sim_old",
        "tmp": "tmp",
        "reports": "reports"
    })
else:
  raise FileNotFoundError("settings.json が見つかりません。設定ファイルを作成してください。")

print(f"project={project}")
print(f"old_version={old_version}")
print(f"new_version={new_version}")

# Export directory paths for downstream scripts
for key, value in directories.items():
    print(f"DIR_{key.upper()}={value}")
