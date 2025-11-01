#!/usr/bin/env python3
"""
========================================================================
                   Stage 4: Validation & Scoring (Verilog)
========================================================================
メトリクスの合否判定を行うスクリプト。

設計方針:
- 閾値は monitor.py で一元管理（METRIC_THRESHOLDS）
- scoreboard.py は判定ロジックのみを実装
"""
  - 一貫性を保つため、閾値の重複定義を排除
"""
import os
import sys
import json

# メトリクスフレームワークのインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from tools.metric_framework import LOWER, HIGHER, NEUTRAL
except ImportError:
    # フレームワークがない場合のフォールバック
    LOWER = "lower_is_better"
    HIGHER = "higher_is_better"
    NEUTRAL = "neutral"

def to_number(v):
    """文字列を数値に変換"""
    if v is None:
        return None
    try:
        s = str(v).strip()
        if s == "":
            return None
        if '.' not in s:
            return int(s)
        return float(s)
    except Exception:
        return None

def load_thresholds_from_monitor():
    """monitor.pyから閾値とメトリクス情報を読み込む"""
    # METRIC_THRESHOLDSを環境変数から取得
    thresholds_json = os.environ.get("METRIC_THRESHOLDS", "{}")
    try:
        thresholds = json.loads(thresholds_json)
    except:
        thresholds = {}
    
    # METRIC_EVALUATIONを環境変数から取得（方向性）
    evaluation_json = os.environ.get("METRIC_EVALUATION", "{}")
    try:
        evaluation = json.loads(evaluation_json)
    except:
        evaluation = {}
    
    return thresholds, evaluation

def evaluate_all_metrics(env_vars, thresholds, evaluation):
    """全メトリクスの合否を判定"""
    failed_metrics = []
    
    for metric_name, threshold_value in thresholds.items():
        # 環境変数からメトリクスの実測値を取得
        actual_value = to_number(env_vars.get(metric_name))
        
        if actual_value is None:
            # メトリクス値が見つからない場合はスキップ（警告のみ）
            print(f"Warning: {metric_name} not available for validation")
            continue
        
        # 評価方向を取得
        direction = evaluation.get(metric_name, LOWER)
        
        # 閾値チェック
        passed = True
        if direction == LOWER:
            # 低い方が良い（latency, error_count など）
            if actual_value > threshold_value:
                passed = False
                print(f"FAIL: {metric_name}={actual_value} exceeds threshold {threshold_value}")
        elif direction == HIGHER:
            # 高い方が良い（coverage, pass_rate など）
            if actual_value < threshold_value:
                passed = False
                print(f"FAIL: {metric_name}={actual_value} below threshold {threshold_value}")
        # NEUTRAL は判定しない
        
        if not passed:
            failed_metrics.append(metric_name)
        else:
            print(f"PASS: {metric_name}={actual_value} (threshold: {threshold_value})")
    
    return len(failed_metrics) == 0, failed_metrics

# ========================================================================================
# MAIN EXECUTION
# ========================================================================================

if __name__ == '__main__':
    # 環境変数を取得
    env_vars = dict(os.environ)
    
    # monitor.pyから閾値情報を読み込む
    thresholds, evaluation = load_thresholds_from_monitor()
    
    if not thresholds:
        print("Warning: No thresholds defined in monitor.py (METRIC_THRESHOLDS)")
        print("All checks passed (no thresholds to validate)")
        sys.exit(0)
    
    print(f"Evaluating {len(thresholds)} metrics with thresholds...")
    
    # 全メトリクスを評価
    passed, failed_metrics = evaluate_all_metrics(env_vars, thresholds, evaluation)
    
    # 後方互換性のため、環境変数にしきい値をエクスポート
    for metric_name, threshold_value in thresholds.items():
        os.environ[f"THRESHOLD_{metric_name.upper()}"] = str(threshold_value)
    
    # 結果を出力
    if passed:
        print("\n✅ All checks passed")
        sys.exit(0)
    else:
        print(f"\n❌ {len(failed_metrics)} metric(s) failed: {', '.join(failed_metrics)}")
        sys.exit(1)
