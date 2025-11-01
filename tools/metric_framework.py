#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メトリクスフレームワーク

このファイルはフレームワーク提供の部品です。通常は編集不要です。
ユーザーが編集するのは scripts/monitor.py です。
"""
import os
import sys
import re
import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Literal


# ============================================================================
# Metric Specification Data Class
# ============================================================================

@dataclass
class MetricSpec:
    """メトリクス仕様の定義"""
    display_name: str
    type: Literal["measured", "comparison"]
    evaluation: Literal["lower_is_better", "neutral", "higher_is_better", "comparison"]


# ============================================================================
# Metric Definition Constants
# ============================================================================

# Type shortcuts
MEASURED = "measured"
COMPARISON = "comparison"

# Evaluation shortcuts
LOWER = "lower_is_better"
NEUTRAL = "neutral"
HIGHER = "higher_is_better"
COMPARE = "comparison"


# ============================================================================
# Metric Base Class (Abstract)
# ============================================================================

class Metric(ABC):
    """
    メトリクスの基底クラス
    
    新しいメトリクスを追加する場合は、このクラスを継承して extract() メソッドを実装してください。
    
    Example:
        class CoverageMetric(Metric):
            def __init__(self):
                super().__init__(
                    name="test_coverage",
                    label="カバレッジ (%)",
                    type=MEASURED,
                    direction=HIGHER,
                    threshold=80.0  # オプション: 閾値を指定
                )
            
            def extract(self, testcase_name, log_dir, log_content):
                coverage_file = f"{log_dir}/{testcase_name}.coverage"
                if os.path.exists(coverage_file):
                    with open(coverage_file) as f:
                        return float(f.read().strip())
                return 0.0
    """
    
    def __init__(self, name: str, label: str, type: str, direction: str, threshold=None):
        self.name = name
        self.label = label
        self.type = type
        self.direction = direction
        self.threshold = threshold  # 閾値（オプション）
    
    @abstractmethod
    def extract(self, testcase_name: str, log_dir: str, log_content: str):
        """メトリクスを抽出（サブクラスで実装）"""
        pass


# ============================================================================
# Built-in Metrics (Framework-provided)
# ============================================================================

class LatencyMetric(Metric):
    """レイテンシ (ms) メトリクス"""
    
    def __init__(self):
        super().__init__(
            name="latency_ms",
            label="レイテンシ (ms)",
            type=MEASURED,
            direction=LOWER,
            threshold=2000  # 2秒以内
        )
    
    def extract(self, testcase_name: str, log_dir: str, log_content: str):
        for line in log_content.split('\n'):
            match = re.match(rf'{testcase_name}:\s*([\d.]+)s', line)
            if match:
                return int(float(match.group(1)) * 1000)
        return 0


class ErrorCountMetric(Metric):
    """エラー数メトリクス"""
    
    def __init__(self):
        super().__init__(
            name="error_count",
            label="エラー数",
            type=MEASURED,
            direction=LOWER,
            threshold=0  # エラーゼロ必須
        )
    
    def extract(self, testcase_name: str, log_dir: str, log_content: str):
        for line in log_content.split('\n'):
            match = re.match(rf'{testcase_name}:.*?(\d+)\s*errors?', line)
            if match:
                return int(match.group(1))
        return 0


class WarningCountMetric(Metric):
    """警告数メトリクス"""
    
    def __init__(self):
        super().__init__(
            name="warning_count",
            label="警告数",
            type=MEASURED,
            direction=LOWER,
            threshold=0  # 例: 警告は許容しない
        )
    
    def extract(self, testcase_name: str, log_dir: str, log_content: str):
        for line in log_content.split('\n'):
            match = re.match(rf'{testcase_name}:.*?(\d+)\s*warnings?', line)
            if match:
                return int(match.group(1))
        return 0


class SignalTransitionsMetric(Metric):
    """信号遷移数メトリクス"""
    
    def __init__(self):
        super().__init__(
            name="signal_transitions",
            label="信号遷移数",
            type=MEASURED,
            direction=LOWER
        )
    
    def extract(self, testcase_name: str, log_dir: str, log_content: str):
        return 0  # TODO: 必要に応じて実装


# ============================================================================
# Framework Functions (Internal)
# ============================================================================

def _set_metric_defaults(metrics: dict, metric_names: List[str]) -> dict:
    """メトリクスのデフォルト値を設定"""
    for metric_name in metric_names:
        if metric_name not in metrics or metrics[metric_name] is None:
            metrics[metric_name] = 0
    return metrics


def _extract_testcase_metrics(metrics_list: List[Metric], testcase_name: str, log_dir: str, log_content: str) -> dict:
    """テストケースから全メトリクスを抽出"""
    metrics = {}
    
    for metric in metrics_list:
        try:
            value = metric.extract(testcase_name, log_dir, log_content)
            metrics[metric.name] = value
        except Exception as e:
            print(f"Warning: Failed to extract {metric.name} for {testcase_name}: {e}", file=sys.stderr)
            metrics[metric.name] = 0
    
    return metrics


def _save_testcase_details_csv(metrics_list: List[Metric], metric_names: List[str]):
    """テストケース別詳細をCSVに保存（新旧データを同じファイルに追記）"""
    log_path = os.getenv("NEW_LOG_PATH", "sim_new/aggregated.log")
    log_dir = os.path.dirname(log_path) or "."
    
    if not os.path.exists(log_path):
        return
    
    # Determine version label
    is_old_version = "sim_old" in log_path
    version_label = "old" if is_old_version else "new"
    
    csv_path = os.path.join("tmp", "verification_metrics.csv")
    os.makedirs("tmp", exist_ok=True)
    
    testcase_rows = []
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Extract testcase names
        testcase_names = []
        for line in log_content.split('\n'):
            match = re.match(r'(\w+):\s*[\d.]+s,\s*\d+\s*errors?', line)
            if match:
                testcase_names.append(match.group(1))
        
        # Extract metrics for each testcase
        for testcase_name in testcase_names:
            all_metrics = _extract_testcase_metrics(metrics_list, testcase_name, log_dir, log_content)
            
            row = {
                "testcase_name": testcase_name,
                "version": version_label
            }
            for metric_name in metric_names:
                row[metric_name] = all_metrics.get(metric_name, 0)
            
            testcase_rows.append(row)
        
        # Read existing CSV if it exists
        existing_rows = []
        if os.path.exists(csv_path):
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Skip rows with the same version (overwrite)
                    if row.get("version") != version_label:
                        existing_rows.append(row)
        
        # Combine existing and new rows
        all_rows = existing_rows + testcase_rows
        
        # Write CSV
        if all_rows:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ["testcase_name", "version"] + metric_names
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_rows)
            
            print(f"# Testcase details saved to: {csv_path}", file=sys.stderr)
    
    except Exception as e:
        print(f"Warning: Failed to save testcase details CSV: {e}", file=sys.stderr)


def process_metrics(metrics_classes: List):
    """
    メトリクスを処理してレポート用に出力
    
    Args:
        metrics_classes: Metricクラスのリスト（クラスまたはインスタンス）
    """
    import json
    
    # Auto-instantiate metric classes
    metric_instances = [
        M() if isinstance(M, type) else M
        for M in metrics_classes
    ]
    
    # Extract metric names
    metric_names = [m.name for m in metric_instances]
    
    # Initialize metrics dictionary
    metrics = {}
    metrics = _set_metric_defaults(metrics, metric_names)
    
    # Build metric specs
    metric_spec: Dict[str, MetricSpec] = {
        m.name: MetricSpec(
            display_name=m.label,
            type=m.type,
            evaluation=m.direction
        )
        for m in metric_instances
    }
    
    # Extract dicts for compatibility
    display_names = {name: spec.display_name for name, spec in metric_spec.items()}
    metric_types = {name: spec.type for name, spec in metric_spec.items()}
    metric_evaluation = {name: spec.evaluation for name, spec in metric_spec.items()}
    
    # Extract thresholds from metric instances
    # Validate: COMPARISON metrics should not have thresholds
    metric_thresholds = {}
    for m in metric_instances:
        if m.threshold is not None:
            if m.type == COMPARISON:
                # Warning: COMPARISON metrics cannot have thresholds
                print(f"Warning: Metric '{m.name}' has type=COMPARISON but threshold={m.threshold} is set. "
                      f"Thresholds are not applicable to comparison metrics and will be ignored.", 
                      file=sys.stderr)
            else:
                # Valid threshold for MEASURED metrics
                metric_thresholds[m.name] = m.threshold
    
    # Determine version
    log_path = os.getenv("NEW_LOG_PATH", "sim_new/aggregated.log")
    is_old_version = "sim_old" in log_path
    

    # Output metrics
    for metric_name in metric_spec.keys():
        spec = metric_spec[metric_name]
        
        # Skip comparison metrics for old version
        if is_old_version and spec.type == COMPARISON:
            continue
        
        value = metrics.get(metric_name, 0)
        print(f"{metric_name}={value}")
    
    # Output metadata as JSON
    print(f"METRIC_DISPLAY_NAMES={json.dumps(display_names, ensure_ascii=False)}")
    print(f"METRIC_TYPES={json.dumps(metric_types, ensure_ascii=False)}")
    print(f"METRIC_EVALUATION={json.dumps(metric_evaluation, ensure_ascii=False)}")
    print(f"METRIC_THRESHOLDS={json.dumps(metric_thresholds, ensure_ascii=False)}")
    
    # Save per-testcase details (include all metrics)
    all_metrics = list(metric_spec.keys())
    _save_testcase_details_csv(metric_instances, all_metrics)
