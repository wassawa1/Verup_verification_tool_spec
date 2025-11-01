#!/usr/bin/env python3
"""
Scoreboard: メトリクスの合否判定
しきい値に基づいて各メトリクスの合否を判定します
"""
import sys
import os

# メトリクスフレームワークのインポート
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from tools.metric_framework import LOWER, HIGHER, NEUTRAL
except ImportError:
    # フレームワークがない場合のフォールバック
    LOWER = "lower_is_better"
    HIGHER = "higher_is_better"
    NEUTRAL = "neutral"

# デフォルトのしきい値設定
# ユーザーは必要に応じてこれらの値を調整できます
DEFAULT_THRESHOLDS = {
    'latency_ms': {'max': 1000, 'direction': LOWER},
    'error_count': {'max': 0, 'direction': LOWER},
    'memory_kb': {'max': 10000, 'direction': LOWER},  # 10MB以下で合格
}

def get_metric_direction(metric_name):
    """メトリクスの評価方向を取得"""
    if metric_name in DEFAULT_THRESHOLDS:
        return DEFAULT_THRESHOLDS[metric_name].get('direction', LOWER)
    return LOWER  # デフォルトは低い方が良い

def evaluate_pass_fail(metrics):
    """メトリクスの合否判定"""
    judgements = {}
    
    for metric_name, value in metrics.items():
        if value is None:
            judgements[metric_name] = '?'
            continue
        
        if metric_name not in DEFAULT_THRESHOLDS:
            # しきい値が定義されていないメトリクスはスキップ
            judgements[metric_name] = '-'
            continue
        
        threshold_config = DEFAULT_THRESHOLDS[metric_name]
        direction = threshold_config.get('direction', LOWER)
        
        try:
            value = float(value)
        except (ValueError, TypeError):
            judgements[metric_name] = '?'
            continue
        
        # 方向に応じた判定
        if direction == LOWER:
            # 低い方が良い（latency, error_count など）
            max_threshold = threshold_config.get('max')
            if max_threshold is not None:
                judgements[metric_name] = 'PASS' if value <= max_threshold else 'FAIL'
            else:
                judgements[metric_name] = '-'
        
        elif direction == HIGHER:
            # 高い方が良い（pass_rate, coverage など）
            min_threshold = threshold_config.get('min')
            if min_threshold is not None:
                judgements[metric_name] = 'PASS' if value >= min_threshold else 'FAIL'
            else:
                judgements[metric_name] = '-'
        
        else:
            # NEUTRAL の場合はしきい値判定しない
            judgements[metric_name] = '-'
    
    # 総合判定: すべての判定対象がPASSなら全体もPASS
    all_pass = all(j == 'PASS' for j in judgements.values() if j in ['PASS', 'FAIL'])
    has_any_judgement = any(j in ['PASS', 'FAIL'] for j in judgements.values())
    judgements['overall'] = 'PASS' if (all_pass and has_any_judgement) else 'FAIL'
    
    return judgements


if __name__ == '__main__':
    import os
    
    # Read metrics from environment variables
    metrics = {}
    for key, value in os.environ.items():
        if key.isupper() and not key.startswith('OLD_'):
            try:
                metrics[key.lower()] = int(value)
            except (ValueError, TypeError):
                metrics[key.lower()] = value
    
    judgements = evaluate_pass_fail(metrics)
    
    # Output in key=value format for run_pipeline.py
    for key, value in judgements.items():
        if value is not None:
            print(f'{key}={value}')
