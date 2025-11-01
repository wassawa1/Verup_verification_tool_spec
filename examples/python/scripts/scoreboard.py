#!/usr/bin/env python3
"""
Scoreboard: メトリクスの合否判定
monitor.pyで定義された閾値に基づいて各メトリクスの合否を判定します
"""
import sys
import os
import json

# メトリクスフレームワークのインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from tools.metric_framework import LOWER, HIGHER, NEUTRAL, COMPARISON
except ImportError:
    # フレームワークがない場合のフォールバック
    LOWER = "lower_is_better"
    HIGHER = "higher_is_better"
    NEUTRAL = "neutral"
    COMPARISON = "comparison"


def load_thresholds_from_monitor():
    """monitor.pyで定義された閾値を環境変数から読み込む"""
    thresholds_json = os.environ.get("METRIC_THRESHOLDS", "{}")
    try:
        thresholds = json.loads(thresholds_json)
        return thresholds
    except json.JSONDecodeError:
        print("Warning: Failed to parse METRIC_THRESHOLDS", file=sys.stderr)
        return {}


def load_metric_evaluation():
    """メトリクスの評価方向を環境変数から読み込む"""
    evaluation_json = os.environ.get("METRIC_EVALUATION", "{}")
    try:
        evaluation = json.loads(evaluation_json)
        return evaluation
    except json.JSONDecodeError:
        print("Warning: Failed to parse METRIC_EVALUATION", file=sys.stderr)
        return {}


def evaluate_all_metrics(env_vars, thresholds, evaluation):
    """すべてのメトリクスを評価して合否判定"""
    print(f"Evaluating {len(thresholds)} metrics with thresholds...")
    
    results = {}
    passed_count = 0
    failed_count = 0
    
    for metric_name, threshold_value in thresholds.items():
        if threshold_value is None:
            continue
            
        # 環境変数から実測値を取得
        actual_value = env_vars.get(metric_name.upper())
        if actual_value is None:
            results[metric_name] = "SKIP"
            continue
        
        try:
            actual_value = float(actual_value)
            threshold_value = float(threshold_value)
        except (ValueError, TypeError):
            results[metric_name] = "ERROR"
            continue
        
        # 評価方向を取得
        direction = evaluation.get(metric_name, LOWER)
        
        # 方向に応じた判定
        passed = False
        if direction == LOWER:
            passed = actual_value <= threshold_value
        elif direction == HIGHER:
            passed = actual_value >= threshold_value
        else:
            # NEUTRAL や COMPARISON は閾値判定しない
            results[metric_name] = "N/A"
            continue
        
        results[metric_name] = "PASS" if passed else "FAIL"
        if passed:
            passed_count += 1
        else:
            failed_count += 1
    
    # 総合判定
    overall = "PASS" if failed_count == 0 and passed_count > 0 else "FAIL"
    results["overall"] = overall
    
    print(f"Results: {passed_count} passed, {failed_count} failed")
    
    return results


if __name__ == '__main__':
    # monitor.pyから閾値と評価方向を読み込む
    thresholds = load_thresholds_from_monitor()
    evaluation = load_metric_evaluation()
    
    # 環境変数からメトリクスを読み込む
    env_vars = {}
    for key, value in os.environ.items():
        if key.isupper() and not key.startswith('OLD_') and not key.startswith('METRIC_'):
            env_vars[key.lower()] = value
    
    # 合否判定を実行
    results = evaluate_all_metrics(env_vars, thresholds, evaluation)
    
    # key=value形式で出力
    for metric_name, result in results.items():
        print(f"{metric_name}={result}")
    
    # 後方互換性のために、閾値をTHRESHOLD_*形式でも出力
    for metric_name, threshold_value in thresholds.items():
        if threshold_value is not None:
            print(f"THRESHOLD_{metric_name.upper()}={threshold_value}")
