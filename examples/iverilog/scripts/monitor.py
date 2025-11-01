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
    WarningCountMetric,
    SignalTransitionsMetric,
    process_metrics,
)

# Import user tools
from user_tools.vcd_utils import (
    count_vcd_signals,
    count_vcd_lines,
    calculate_vcd_similarity,
)


# ============================================================================
# User-defined VCD Metrics (using user_tools/vcd_utils.py)
# ============================================================================

class VcdSignalsMetric(Metric):
    """VCD信号数メトリクス"""
    
    def __init__(self):
        super().__init__(
            name="vcd_signals",
            label="VCD信号数",
            type=MEASURED,
            direction=NEUTRAL,
            threshold=0
        )
    
    def extract(self, testcase_name, log_dir, log_content):
        """VCDファイルから信号数を抽出"""
        vcd_path = os.path.join(log_dir, f"{testcase_name}.vcd")
        if os.path.exists(vcd_path):
            return count_vcd_signals(vcd_path) or 0
        return 0


class VcdLinesMetric(Metric):
    """VCDファイル行数メトリクス"""
    
    def __init__(self):
        super().__init__(
            name="vcd_lines",
            label="VCDファイル行数",
            type=MEASURED,
            direction=NEUTRAL,
            threshold=0
        )
    
    def extract(self, testcase_name, log_dir, log_content):
        """VCDファイルの行数を抽出"""
        vcd_path = os.path.join(log_dir, f"{testcase_name}.vcd")
        if os.path.exists(vcd_path):
            return count_vcd_lines(vcd_path) or 0
        return 0


class VcdSizeMetric(Metric):
    """VCDファイルサイズメトリクス"""
    
    def __init__(self):
        super().__init__(
            name="vcd_size_kb",
            label="VCDファイルサイズ (KB)",
            type=MEASURED,
            direction=NEUTRAL,
        )
    
    def extract(self, testcase_name, log_dir, log_content):
        """VCDファイルのサイズを抽出"""
        vcd_path = os.path.join(log_dir, f"{testcase_name}.vcd")
        if os.path.exists(vcd_path):
            return round(os.path.getsize(vcd_path) / 1024.0, 2)
        return 0.0


class VcdSimilarityMetric(Metric):
    """波形一致性メトリクス（比較）"""
    
    def __init__(self):
        super().__init__(
            name="vcd_similarity",
            label="波形一致性",
            type=COMPARISON,
            direction=COMPARE
        )
    
    def extract(self, testcase_name, log_dir, log_content):
        """新旧VCDファイルを比較して一致性を計算"""
        # Get old and new VCD paths from environment
        old_log_dir = os.getenv("OLD_LOG_PATH", "sim_old/aggregated.log")
        old_log_dir = os.path.dirname(old_log_dir) or "sim_old"
        
        new_vcd_path = os.path.join(log_dir, f"{testcase_name}.vcd")
        old_vcd_path = os.path.join(old_log_dir, f"{testcase_name}.vcd")
        
        # Compare VCD files if both exist
        if os.path.exists(new_vcd_path) and os.path.exists(old_vcd_path):
            similarity = calculate_vcd_similarity(new_vcd_path, old_vcd_path)
            return similarity if similarity is not None else 0.0
        
        return 0.0


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
    WarningCountMetric,
    SignalTransitionsMetric,
    # User-defined VCD metrics
    VcdSignalsMetric,
    VcdLinesMetric,
    VcdSizeMetric,
    VcdSimilarityMetric,
]


def main():
    process_metrics(METRICS)


if __name__ == "__main__":
    main()
