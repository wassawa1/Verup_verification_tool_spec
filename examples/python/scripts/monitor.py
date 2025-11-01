#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metrics Validation and Normalization Script

User Customization File

Add new metrics by:
Step 1: Define a Metric subclass
Step 2: Add class to METRICS list (no () needed)
"""
import os
import sys
import io

# Set UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import framework components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from tools.metric_framework import (
    Metric,
    MEASURED, COMPARISON,
    LOWER, NEUTRAL, HIGHER, COMPARE,
    LatencyMetric,
    ErrorCountMetric,
    process_metrics,
)


# ============================================================================
# Custom Metric: Memory Usage
# ============================================================================

class MemoryUsageMetric(Metric):
    """メモリ使用量メトリクス（低いほど良い）"""
    
    def __init__(self):
        super().__init__(
            name="memory_kb",
            label="メモリ使用量 (KB)",
            type=MEASURED,
            direction=LOWER  # Lower is better
        )
    
    def extract(self, testcase_name, log_dir, log_content):
        """ログからメモリ使用量を抽出
        
        driver.pyで測定されたメモリ使用量を読み取ります。
        例: "calculator: 0.053s, 0 errors, 1234 KB"
        """
        import re
        
        # aggregated.logから該当行を検索
        for line in log_content.split('\n'):
            # パターン: "testcase_name: X.XXXs, X errors, XXXX KB"
            match = re.match(rf'{testcase_name}:.*?(\d+)\s*KB', line, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # メモリ情報が見つからない場合は0を返す
        return 0


# ============================================================================
# METRICS List
# ============================================================================
# 
# 閾値の指定方法（任意）:
# メトリクス定義時に threshold パラメータを追加できます。
# 
# 例:
#   class MyMetric(Metric):
#       def __init__(self):
#           super().__init__(
#               name="my_metric",
#               label="My Metric",
#               type=MEASURED,
#               direction=LOWER,
#               threshold=100  # ← 閾値を指定（任意）
#           )
# 
# 閾値が指定されたメトリクスは、レポートに自動的に閾値列が表示されます。
# scoreboard.pyでの定義も可能ですが、monitor.pyでの定義が優先されます。
# ============================================================================

METRICS = [
    # Framework-provided basic metrics
    LatencyMetric,
    ErrorCountMetric,
    # User-defined memory metric
    MemoryUsageMetric,
]

def main():
    process_metrics(METRICS)


if __name__ == "__main__":
    main()
