#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================
                   Stage 1: Environment Setup
========================================================================
環境変数とプロジェクト設定を定義するスクリプト。

カスタマイズポイント:
1. settings.jsonの読み込み
2. プロジェクト固有の環境変数設定
3. バージョン情報の設定

出力形式:
  標準出力に key=value 形式で環境変数を出力
  例: project=my-project
      old_version=1.0.0
      new_version=2.0.0
========================================================================
"""
import os
import sys
import json
from pathlib import Path


def load_settings():
    """
    settings.jsonからプロジェクト設定を読み込む
    
    Returns:
        dict: 設定情報
    """
    settings_file = Path(__file__).parent / "settings.json"
    
    if not settings_file.exists():
        print(f"Error: {settings_file} not found", file=sys.stderr)
        sys.exit(1)
    
    with open(settings_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def setup_directories():
    """
    必要なディレクトリを作成
    
    カスタマイズポイント:
    - プロジェクトで必要なディレクトリを追加
    """
    directories = [
        "testcases",
        "sim_new",
        "sim_old",
        "tmp",
        "reports"
    ]
    
    for d in directories:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"DIR_{d.upper()}={d}")


def main():
    """
    メイン処理
    
    カスタマイズ手順:
    1. settings.jsonを編集（プロジェクト名、バージョン）
    2. 必要に応じて追加の環境変数を定義
    3. プロジェクト固有の初期化処理を追加
    """
    # 設定読み込み
    settings = load_settings()
    
    # 基本情報を出力
    print(f"project={settings.get('project', 'unknown')}")
    print(f"old_version={settings.get('old_version', '1.0.0')}")
    print(f"new_version={settings.get('new_version', '2.0.0')}")
    
    # ディレクトリ作成
    setup_directories()
    
    # ========================================
    # カスタマイズエリア: プロジェクト固有の環境変数
    # ========================================
    # 例: コンパイラパス、ライブラリパスなど
    # print(f"COMPILER_PATH=/usr/bin/gcc")
    # print(f"LIB_PATH=/usr/local/lib")


if __name__ == "__main__":
    main()
