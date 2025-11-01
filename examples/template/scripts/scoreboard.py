#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================
                   Stage 4: Validation & Scoring
========================================================================
メトリクスを評価し、Pass/Failを判定するスクリプト。

カスタマイズポイント:
1. 閾値の設定
2. 判定ロジック
3. カスタム評価基準

出力形式:
  標準出力に key=value 形式で結果を出力
  例: latency_ms=PASS
      error_count=PASS
      overall=PASS
      THRESHOLD_LATENCY_MS=2000
      THRESHOLD_ERROR_COUNT=0
========================================================================
"""
import os
import sys


def get_thresholds():
    """
    閾値を取得（環境変数から動的に取得）
    
    カスタマイズポイント:
    - デフォルト閾値の変更
    - 新しい閾値の追加
    
    Returns:
        dict: {metric_name: threshold_value}
    """
    # 環境変数METRIC_THRESHOLDSからJSON形式で取得
    import json
    thresholds_json = os.environ.get("METRIC_THRESHOLDS", "{}")
    
    try:
        thresholds = json.loads(thresholds_json)
    except:
        # フォールバック: デフォルト閾値
        thresholds = {}
    
    # ========================================
    # カスタマイズ: デフォルト閾値
    # ========================================
    # monitor.pyで定義されていない場合のフォールバック
    if not thresholds:
        thresholds = {
            "latency_ms": 2000,      # 2秒以内
            "error_count": 0,        # エラーなし
            # "custom_metric": 1000, # カスタム閾値を追加
        }
    
    return thresholds


def evaluate_metric(metric_name, value, threshold, direction="lower_is_better"):
    """
    単一メトリクスを評価
    
    カスタマイズポイント:
    - 評価ロジックの変更
    - 複雑な判定基準の追加
    
    Args:
        metric_name: メトリクス名
        value: 実測値
        threshold: 閾値
        direction: 評価方向（lower_is_better/higher_is_better）
        
    Returns:
        str: "PASS", "FAIL", or "SKIP"
    """
    if value is None or threshold is None:
        return "SKIP"
    
    try:
        value = float(value)
        threshold = float(threshold)
    except (ValueError, TypeError):
        return "SKIP"
    
    # ========================================
    # カスタマイズ: 評価ロジック
    # ========================================
    
    if direction == "lower_is_better":
        # 低いほど良い（レイテンシ、エラー数など）
        return "PASS" if value <= threshold else "FAIL"
    
    elif direction == "higher_is_better":
        # 高いほど良い（カバレッジ、スコアなど）
        return "PASS" if value >= threshold else "FAIL"
    
    else:
        # 中立（参考値）
        return "SKIP"


def main():
    """
    メイン処理
    
    処理フロー:
    1. 環境変数からメトリクス値を取得
    2. 閾値と比較して評価
    3. 総合判定（overall）を決定
    4. 結果を標準出力に出力
    """
    # 閾値取得
    thresholds = get_thresholds()
    
    # メトリクス評価方向を取得
    import json
    evaluation_json = os.environ.get("METRIC_EVALUATION", "{}")
    try:
        evaluations = json.loads(evaluation_json)
    except:
        evaluations = {}
    
    print(f"Evaluating {len(thresholds)} metrics with thresholds...", file=sys.stderr)
    
    # 各メトリクスを評価
    results = {}
    passed = 0
    failed = 0
    
    for metric_name, threshold in thresholds.items():
        # 環境変数からメトリクス値を取得
        value = os.environ.get(metric_name)
        direction = evaluations.get(metric_name, "lower_is_better")
        
        # 評価
        result = evaluate_metric(metric_name, value, threshold, direction)
        results[metric_name] = result
        
        if result == "PASS":
            passed += 1
            print(f"PASS: {metric_name}={value} (threshold: {threshold})", file=sys.stderr)
        elif result == "FAIL":
            failed += 1
            print(f"FAIL: {metric_name}={value} (threshold: {threshold})", file=sys.stderr)
    
    print(f"Results: {passed} passed, {failed} failed", file=sys.stderr)
    
    # ========================================
    # カスタマイズ: 総合判定ロジック
    # ========================================
    # デフォルト: FAILが1つでもあれば全体FAIL
    overall = "PASS" if failed == 0 else "FAIL"
    
    # 他の判定例:
    # - 特定のメトリクスだけ重視
    # - FAIL数が一定数以下ならPASS
    # - 重み付け評価
    
    # 結果を標準出力に出力
    for metric_name, result in results.items():
        print(f"{metric_name}={result}")
    
    print(f"overall={overall}")
    
    # 閾値も出力（レポート生成で使用）
    for metric_name, threshold in thresholds.items():
        print(f"THRESHOLD_{metric_name.upper()}={threshold}")


if __name__ == "__main__":
    main()
