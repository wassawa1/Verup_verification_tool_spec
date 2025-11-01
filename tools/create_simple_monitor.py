#!/usr/bin/env python3
# Helper script to create simplified monitor.py
import os

MONITOR_CONTENT = '''#!/usr/bin/env python3
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
    VcdSignalsMetric,
    VcdLinesMetric,
    VcdSizeMetric,
    VcdSimilarityMetric,
    process_metrics,
)

# ============================================================================
# METRICS List
# ============================================================================

METRICS = [
    LatencyMetric,
    ErrorCountMetric,
    WarningCountMetric,
    SignalTransitionsMetric,
    VcdSignalsMetric,
    VcdLinesMetric,
    VcdSizeMetric,
    VcdSimilarityMetric,
]


def main():
    process_metrics(METRICS)


if __name__ == "__main__":
    main()
'''

if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'monitor.py')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(MONITOR_CONTENT)
    print(f"Created: {output_path}")
