#!/usr/bin/env python3
import os
import sys

# Import framework components
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from tools.metric_framework import (
    Metric,
    MEASURED,
    LOWER,
    HIGHER,
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

# Basic metrics for simple Python test example
METRICS = [
    LatencyMetric,        # Execution time in milliseconds
    ErrorCountMetric,     # Number of test failures
    MemoryUsageMetric,    # Custom: Memory usage in KB (lower is better)
]

def main():
    process_metrics(METRICS)

if __name__ == '__main__':
    main()
