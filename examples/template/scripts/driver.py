#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================
                   Stage 2: Test Execution Driver
========================================================================
テストケースを実行し、ログを生成するスクリプト。

カスタマイズポイント:
1. テストケースの検索ロジック
2. テスト実行コマンド（コンパイル、実行）
3. ログ出力形式
4. パフォーマンス測定方法

出力形式:
  標準出力に key=value 形式でメトリクスを出力
  例: latency_ms=1500
      error_count=0
      testcases_count=5

ログファイル:
  {output_dir}/aggregated.log にテスト結果を集約
  フォーマット: "testcase_name: X.XXs, X errors"
========================================================================
"""
import os
import sys
import time
import subprocess
from pathlib import Path


def find_testcases(testcases_dir="testcases"):
    """
    テストケースを検索
    
    カスタマイズポイント:
    - ファイル拡張子を変更（.py, .cpp, .v, .vhdlなど）
    - 除外パターンの追加
    
    Args:
        testcases_dir: テストケースディレクトリ
        
    Returns:
        list: テストケースファイルのリスト
    """
    testcases = []
    testcase_path = Path(testcases_dir)
    
    if not testcase_path.exists():
        print(f"Error: {testcases_dir} not found", file=sys.stderr)
        return testcases
    
    # ========================================
    # カスタマイズ: ファイル拡張子を指定
    # ========================================
    # Python: "*.py"
    # Verilog: "*.v"
    # C++: "*.cpp"
    # など
    patterns = ["*.py"]  # <- ここを変更
    
    for pattern in patterns:
        testcases.extend(sorted(testcase_path.glob(pattern)))
    
    return testcases


def execute_testcase(testcase_file, output_dir):
    """
    単一のテストケースを実行
    
    カスタマイズポイント:
    - コンパイルコマンド
    - 実行コマンド
    - タイムアウト設定
    - エラー検出方法
    
    Args:
        testcase_file: テストケースファイルのパス
        output_dir: 出力ディレクトリ
        
    Returns:
        dict: {
            'name': テストケース名,
            'latency': 実行時間(秒),
            'errors': エラー数,
            'success': 成功/失敗
        }
    """
    testcase_name = testcase_file.stem
    result = {
        'name': testcase_name,
        'latency': 0.0,
        'errors': 0,
        'success': False
    }
    
    print(f"  {testcase_name}...", file=sys.stderr)
    
    # ========================================
    # カスタマイズ: テスト実行コマンド
    # ========================================
    
    # 例1: Pythonスクリプトの実行
    # start_time = time.time()
    # try:
    #     proc = subprocess.run(
    #         ['python3', str(testcase_file)],
    #         capture_output=True,
    #         text=True,
    #         timeout=60
    #     )
    #     result['latency'] = time.time() - start_time
    #     result['errors'] = 1 if proc.returncode != 0 else 0
    #     result['success'] = proc.returncode == 0
    # except subprocess.TimeoutExpired:
    #     result['errors'] = 1
    
    # 例2: Verilogシミュレーション（Icarus Verilog）
    # # コンパイル
    # vvp_file = f"{output_dir}/{testcase_name}.vvp"
    # subprocess.run(['iverilog', '-o', vvp_file, str(testcase_file)])
    # # 実行
    # start_time = time.time()
    # proc = subprocess.run(['vvp', vvp_file], capture_output=True)
    # result['latency'] = time.time() - start_time
    # result['errors'] = 1 if proc.returncode != 0 else 0
    
    # 例3: C++コンパイル・実行
    # # コンパイル
    # exe_file = f"{output_dir}/{testcase_name}"
    # subprocess.run(['g++', '-o', exe_file, str(testcase_file)])
    # # 実行
    # start_time = time.time()
    # proc = subprocess.run([exe_file], capture_output=True)
    # result['latency'] = time.time() - start_time
    # result['errors'] = 1 if proc.returncode != 0 else 0
    
    # ========================================
    # TODO: 上記から適切な実行方法を選択・実装
    # ========================================
    
    # デフォルト実装（ダミー）
    start_time = time.time()
    time.sleep(0.1)  # 実際の実行に置き換える
    result['latency'] = time.time() - start_time
    result['errors'] = 0
    result['success'] = True
    
    return result


def aggregate_results(results, output_dir):
    """
    テスト結果を集約してログファイルに出力
    
    カスタマイズポイント:
    - ログフォーマット
    - 追加メトリクスの出力
    
    Args:
        results: テスト結果のリスト
        output_dir: 出力ディレクトリ
    """
    log_file = Path(output_dir) / "aggregated.log"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        for result in results:
            # フォーマット: "testcase_name: X.XXXs, X errors"
            line = f"{result['name']}: {result['latency']:.3f}s, {result['errors']} errors"
            f.write(line + "\n")
    
    print(f"[driver] Aggregated log: {log_file}", file=sys.stderr)


def main():
    """
    メイン処理
    
    処理フロー:
    1. 環境変数から出力ディレクトリを取得
    2. テストケースを検索
    3. 各テストケースを実行
    4. 結果を集約
    5. メトリクスを標準出力に出力
    """
    # 出力ディレクトリ（環境変数から取得）
    output_dir = os.environ.get('DIR_SIM_NEW', 'sim_new')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # テストケース検索
    testcases = find_testcases()
    
    if not testcases:
        print("Error: No testcases found", file=sys.stderr)
        sys.exit(1)
    
    print(f"[driver] Processing {len(testcases)} testcases", file=sys.stderr)
    
    # テスト実行
    results = []
    for testcase_file in testcases:
        result = execute_testcase(testcase_file, output_dir)
        results.append(result)
    
    # 結果集約
    aggregate_results(results, output_dir)
    
    # メトリクス計算
    total_latency = sum(r['latency'] for r in results) * 1000  # ms
    total_errors = sum(r['errors'] for r in results)
    
    # 標準出力にメトリクスを出力
    print(f"latency_ms={int(total_latency)}")
    print(f"error_count={total_errors}")
    print(f"testcases_count={len(results)}")


if __name__ == "__main__":
    main()
