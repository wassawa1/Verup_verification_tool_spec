#!/usr/bin/env python3
"""Export a verification report from simulation logs.

========================================================================
                   🔧 フレームワーク提供ツール
========================================================================
このファイルは**フレームワークが提供する汎用部品**です。
基本的にユーザーは編集する必要がありません。

機能：
- メトリクスの動的発見（環境変数から自動検出）
- バージョン比較レポート生成
- テストケース別詳細表示
- Markdown/JSON形式での出力

========================================================================
                         使用箇所 (Used by)
========================================================================
- run_pipeline.py (Stage 4: Validation & Reporting)
  - レポート生成（Markdown/JSON形式）
  - メトリクス動的発見・比較
  - テストケース別詳細表示

依存関係:
  - tmp/testcase_details.csv (scripts/monitor.py が生成)
  - 環境変数 METRIC_DISPLAY_NAMES, METRIC_TYPES, METRIC_EVALUATION
    (scripts/monitor.py が出力)

========================================================================
                          DESIGN PHILOSOPHY
========================================================================
This tool is COMPLETELY TOOL-CONTROLLED and ZERO HARDCODING:

1. NO METRIC NAMES HARDCODED IN CODE
   - All metrics are discovered dynamically from environment variables
   - New metrics added to monitor.py automatically appear in reports
   - Pattern: lowercase with underscore (e.g., latency_ms, error_count)

2. PURE ENVIRONMENT VARIABLE SCANNING
   - Scans combined_env for all lowercase_metric patterns
   - OLD_ prefix for old version metrics (converted to lowercase)
   - No individual variable assignments per metric

3. DISPLAY NAMES FROM MONITOR.PY
   - monitor.py outputs METRIC_DISPLAY_NAMES as JSON
   - export_report.py reads this JSON and applies display names
   - New metrics get auto-generated display name if not in monitor.py
   - ZERO hardcoded display names in export_report.py

4. EXTENSIBILITY
   - Users modify: monitor.py (add new metrics)
   - Users modify: scoreboard.py (add thresholds)
   - This file: NEVER touched by users
   - When monitor.py outputs new metric → auto appears in reports

5. VERSION COMPARISON
   - Metrics passed via environment: latency_ms, error_count, etc.
   - Old metrics passed with OLD_ prefix: OLD_LATENCY_MS, OLD_ERROR_COUNT, etc.
   - Context dict contains: metrics dict + old_metrics dict
   - Report automatically shows comparison table when old_metrics exist

Environment variables flow:
  run_pipeline.py Stage 2 → driver.py outputs latency/errors
  run_pipeline.py Stage 3 → monitor.py extracts/calculates all metrics
  run_pipeline.py adds OLD_ prefix to old version metrics
  run_pipeline.py writes to tmp/stage4_env.txt for subprocess isolation
  export_report.py reads from STAGE4_ENV_FILE and os.environ
  All metrics flow through as-is (no filtering or hardcoding)

This tool generates:
 - Markdown report to <out_dir>/report-<timestamp>.md
 - CSV data from monitor.py (tmp/testcase_details.csv)
 - Metrics from environment + optional log files as fallback
========================================================================
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import re
from typing import Optional, Any


def to_number(v: Optional[str]) -> Optional[Any]:
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    try:
        if '.' not in s and 'e' not in s.lower():
            return int(s)
        return float(s)
    except Exception:
        try:
            return float(s)
        except Exception:
            return None


def extract_metrics_from_log(log_file: str) -> dict:
    """Extract all metrics from log file"""
    metrics = {
        "latency": None,
        "errors": None,
        "warnings": None,
        "vcd_size_kb": None,
        "signal_transitions": None,
        "vcd_signals": None,
        "vcd_lines": None,
    }
    
    if not os.path.exists(log_file):
        return metrics
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract latency (from "Total latency: X.XXXs" format)
        latency_match = re.search(r'Total latency:\s*([\d.]+)\s*s', content)
        if latency_match:
            latency_sec = float(latency_match.group(1))
            metrics["latency"] = int(latency_sec * 1000)
        
        # Extract errors
        error_match = re.search(r'Total errors:\s*(\d+)', content)
        if error_match:
            metrics["errors"] = int(error_match.group(1))
        
        # Extract warnings
        warning_match = re.search(r'Total warnings:\s*(\d+)', content)
        if warning_match:
            metrics["warnings"] = int(warning_match.group(1))
        
        # Extract VCD metrics
        vcd_size_match = re.search(r'VCD file size:\s*([\d.]+)\s*KB', content)
        if vcd_size_match:
            metrics["vcd_size_kb"] = float(vcd_size_match.group(1))
        
        transitions_match = re.search(r'Signal transitions:\s*(\d+)', content)
        if transitions_match:
            metrics["signal_transitions"] = int(transitions_match.group(1))
    
    except Exception as e:
        print(f"Warning: Failed to parse log file {log_file}: {e}", file=__import__('sys').stderr)
    
    return metrics


def decide(lat, err, thr_lat, thr_err):
    ok = True
    messages = []
    if lat is None:
        messages.append("No latency metric available")
        ok = False
    elif lat > thr_lat:
        messages.append(f"Latency too high: {lat} > {thr_lat}")
        ok = False
    if err is None:
        messages.append("No error metric available")
        ok = False
    elif err > thr_err:
        messages.append(f"Errors detected: {err} > {thr_err}")
        ok = False
    return ok, messages


def _load_testcase_details_csv() -> dict:
    """
    CSVファイルから各テストケースの詳細を読み込む（新旧両方）
    
    Returns:
        {
            testcase_name: {
                "new": {metric1: value1, ...},
                "old": {metric1: value1, ...}
            }
        }
    """
    csv_path = os.path.join("tmp", "testcase_details.csv")
    
    testcase_details = {}
    
    if not os.path.exists(csv_path):
        return testcase_details
    
    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                testcase_name = row.get("testcase_name", "")
                version = row.get("version", "new")  # "old" or "new"
                
                if not testcase_name:
                    continue
                
                # Extract metric values
                details = {}
                for key, value in row.items():
                    if key in ["testcase_name", "version"]:
                        continue
                    num_value = to_number(value)
                    details[key] = num_value if num_value is not None else value
                
                # Initialize testcase entry if needed
                if testcase_name not in testcase_details:
                    testcase_details[testcase_name] = {"new": {}, "old": {}}
                
                # Store under appropriate version
                testcase_details[testcase_name][version] = details
    
    except Exception as e:
        print(f"Warning: Failed to load testcase details CSV: {e}", file=__import__('sys').stderr)
    
    return testcase_details


def build_markdown_report(context):
    """
    Build a comprehensive Markdown report from context dict.
    
    DESIGN NOTE - DYNAMIC RENDERING (NO PER-METRIC HARDCODING):
    - all_metrics: [(metric_name, display_name), ...]
    - Iterates over all_metrics (discovered, not hardcoded)
    - For each metric, looks up values in context['metrics'] and context['old_metrics']
    - If old_metrics exist, shows comparison table (旧 vs 新)
    - If no old_metrics, shows single-column table
    - Evaluation logic is metric-semantic aware:
      * latency_ms, error_count, warning_count, signal_transitions: lower is better
      * vcd_similarity: higher is better
      * Others: neutral (no change is good)
    
    This means:
    - Adding new metric to monitor.py → auto appears in report
    - No code changes needed for new metrics
    - Rendering handles dynamic metric count
    """
    lines = []
    
    # Header
    lines.append("# 🔍 Version Upgrade Verification Report\n")
    generated_at = context['generated_at']
    
    # Extract readable date
    try:
        dt = datetime.datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
        readable_date = dt.strftime("%Y年%m月%d日 %H:%M:%S")
    except:
        readable_date = generated_at
    
    lines.append(f"**生成日時**: {readable_date}\n")
    
    # Overview - Large and prominent
    result_icon = "✅ **PASSED**" if context['passed'] else "❌ **FAILED**"
    lines.append(f"## 検証結果: {result_icon}\n")
    
    # Test environment info (Detailed)
    if context.get('project'):
        lines.append("## 📋 テスト環境\n")
        lines.append(f"| 項目 | 値 |")
        lines.append("|:---|:---|")
        lines.append(f"| **プロジェクト** | {context.get('project', 'N/A')} |")
        lines.append(f"| **旧バージョン** | {context.get('old_version', 'N/A')} |")
        lines.append(f"| **新バージョン** | {context.get('new_version', 'N/A')} |")
        if context.get('testcases_count'):
            lines.append(f"| **テストケース数** | {context.get('testcases_count')} |")
        
    
    # Add per-testcase details section (NO AGGREGATION)
    testcase_details = context.get('testcase_details')
    if testcase_details:
        all_metrics = context.get('all_metrics', [])
        metric_types = context.get('metric_types', {})
        lines.append("\n## 📝 テストケース別詳細\n")
        
        # Get metric display names for dynamic column headers
        display_names = {name: disp for name, disp in all_metrics}
        
        # Get thresholds
        threshold_latency = context.get('threshold_latency', 'N/A')
        threshold_errors = context.get('threshold_errors', 'N/A')
        
        for testcase_name in sorted(testcase_details.keys()):
            tc_data = testcase_details[testcase_name]
            new_details = tc_data.get("new", {})
            old_details = tc_data.get("old", {})
            has_old_data = bool(old_details)
            
            lines.append(f"\n### {testcase_name}\n")
            
            # Show old/new comparison if old data available
            if has_old_data:
                lines.append("| 項目 | 旧バージョン | 新バージョン | 閾値 | 判定 |")
                lines.append("|:---|---:|---:|---:|:---:|")
            else:
                lines.append("| 項目 | 値 | 閾値 | 判定 |")
                lines.append("|:---|---:|---:|:---:|")
            
            # Display all metrics dynamically
            for metric_key in new_details.keys():
                new_value = new_details.get(metric_key)
                old_value = old_details.get(metric_key) if has_old_data else None
                
                display_name = display_names.get(metric_key, metric_key.replace("_", " ").title())
                metric_type = metric_types.get(metric_key, "measured")
                
                # Format values
                def format_value(val):
                    if val is None:
                        return "—"
                    if isinstance(val, float):
                        if "size" in metric_key or "kb" in metric_key:
                            return f"{val:.2f} KB"
                        elif "similarity" in metric_key:
                            return f"{val:.1f}%"
                        else:
                            return f"{val:.2f}"
                    elif isinstance(val, int):
                        if val > 1000:
                            return f"{val:,}"
                        elif "ms" in metric_key or "latency" in metric_key:
                            return f"{val} ms"
                        else:
                            return f"{val}"
                    else:
                        return f"{val}"
                
                # For comparison metrics, show "—" in both old/new columns
                if metric_type == "comparison":
                    old_str = "—"
                    new_str = "—"
                    # Determine pass/fail for comparison metrics (e.g., similarity >= 100%)
                    if isinstance(new_value, (int, float)):
                        judgment = "○" if new_value >= 100.0 else "✗"
                    else:
                        judgment = "○"
                else:
                    new_str = format_value(new_value)
                    old_str = format_value(old_value) if has_old_data else None
                    
                    # Determine pass/fail for measured metrics
                    judgment = "○"  # Default pass
                    if "latency" in metric_key or "ms" in metric_key:
                        if isinstance(new_value, (int, float)) and new_value > threshold_latency:
                            judgment = "✗"
                    elif "error" in metric_key:
                        if isinstance(new_value, (int, float)) and new_value > threshold_errors:
                            judgment = "✗"
                
                # Determine threshold
                if "latency" in metric_key or "ms" in metric_key:
                    threshold_str = f"{threshold_latency} ms"
                elif "error" in metric_key:
                    threshold_str = f"{threshold_errors}"
                else:
                    threshold_str = "—"
                
                if has_old_data:
                    lines.append(f"| **{display_name}** | {old_str} | {new_str} | {threshold_str} | {judgment} |")
                else:
                    lines.append(f"| **{display_name}** | {new_str} | {threshold_str} | {judgment} |")
            
            lines.append("")
    
    # Conclusion
    lines.append("\n## 🎯 結論\n")
    if context['passed']:
        lines.append("✅ **検証に合格しました**\n")
        lines.append("新バージョンは指定された閾値内で正常に動作しています。")
    else:
        lines.append("❌ **検証に不合格です**\n")
        lines.append("以下の項目が閾値を超過しています：\n")
        if context.get('messages'):
            for m in context['messages']:
                lines.append(f"- {m}")
    
    lines.append("\n")
    
    # Metadata
    lines.append("---\n")
    lines.append("### 📝 メタ情報\n")
    lines.append(f"- **生成日時**: {readable_date}")
    lines.append(f"- **タイムスタンプ**: {generated_at}\n")

    return "\n".join(lines)


def build_json_report(context):
    return json.dumps(context, ensure_ascii=False, indent=2)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def main():
    p = argparse.ArgumentParser(description="Generate verification report from simulation results")
    p.add_argument("--out", "-o", help="Output file path (if omitted a default file will be created inside --out-dir)")
    p.add_argument("--out-dir", "-d", default="reports", help="Output directory for reports and logs (default: reports)")
    p.add_argument("--format", "-f", choices=["md", "json"], default="md", help="Report format")
    args = p.parse_args()

    # ========================================================================
    # STEP 1: LOAD ENVIRONMENT VARIABLES
    # ========================================================================
    # Split into two sources:
    #  1. tmp/stage4_env.txt: Passed from run_pipeline.py (all metrics)
    #  2. os.environ: Direct process environment
    # This ensures metrics survive subprocess isolation
    # ========================================================================
    
    env_from_file = {}
    env_file_path = os.environ.get("STAGE4_ENV_FILE")
    if env_file_path and os.path.exists(env_file_path):
        try:
            with open(env_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        env_from_file[key.strip()] = value.strip()
        except Exception:
            pass
    
    # Merge: file vars override os.environ (file is more recent)
    combined_env = dict(os.environ)
    combined_env.update(env_from_file)
    
    # ========================================================================
    # STEP 2: DYNAMIC METRIC EXTRACTION - NO HARDCODING
    # ========================================================================
    # RULE: Metric = lowercase env var with underscore, not prefixed with OLD_
    # Example: latency_ms=730, error_count=0, vcd_similarity=100.0
    # Old metrics have OLD_ prefix: OLD_LATENCY_MS=728, OLD_ERROR_COUNT=0
    # 
    # This pattern-based approach means:
    # - Zero metric names hardcoded
    # - New metrics from monitor.py auto-discovered
    # - No if-statements filtering specific metrics
    # ========================================================================
    
    metrics = {}           # New version: {latency_ms: 730, error_count: 0, ...}
    old_metrics = {}       # Old version: {latency_ms: 728, error_count: 0, ...}
    metric_order = []      # Track discovery order for consistent display
    
    # METRIC SCANNING: Find all metrics by pattern matching
    for env_key, env_value in combined_env.items():
        # NEW VERSION METRICS: Pattern = lowercase_name_with_underscores
        # Examples: latency_ms, error_count, warning_count, vcd_signals, etc.
        if len(env_key) > 0 and env_key[0].islower() and "_" in env_key and not env_key.startswith("OLD_"):
            value = to_number(env_value)
            if value is not None:
                metrics[env_key] = value
                if env_key not in metric_order:
                    metric_order.append(env_key)
        
        # OLD VERSION METRICS: Pattern = OLD_UPPERCASE_METRIC_NAME
        # Run_pipeline.py adds OLD_ prefix: OLD_LATENCY_MS=728, OLD_ERROR_COUNT=0
        # Convert to lowercase for consistency with new metrics
        if env_key.startswith("OLD_"):
            remainder = env_key[4:].lower()  # Strip OLD_ and lowercase
            if remainder and "_" in remainder:  # Must match metric pattern
                metric_name = remainder
                value = to_number(env_value)
                if value is not None:
                    old_metrics[metric_name] = value
    
    # ========================================================================
    # STEP 3: FALLBACK - IF NO METRICS, TRY LOG FILES
    # ========================================================================
    # Used only if subprocess env var passing fails
    # This is a safety net, not the primary path
    # ========================================================================
    
    if not metrics:
        new_log_path = combined_env.get("NEW_LOG_PATH", "sim_new/aggregated.log")
        if os.path.exists(new_log_path):
            log_metrics = extract_metrics_from_log(new_log_path)
            for key, value in log_metrics.items():
                if value is not None:
                    metrics[key] = value
                    if key not in metric_order:
                        metric_order.append(key)
    
    # ========================================================================
    # STEP 4: EXTRACT INFRASTRUCTURE VARIABLES (NON-METRICS)
    # ========================================================================
    # These are NOT discovered dynamically - they're infrastructure:
    #  - THRESHOLD_LATENCY, THRESHOLD_ERRORS (from scoreboard.py)
    #  - PROJECT, OLD_VERSION, NEW_VERSION (from envs.py)
    #  - TESTCASES_COUNT (from driver.py)
    # ========================================================================
    
    thr_lat = to_number(combined_env.get("THRESHOLD_LATENCY")) or 2000
    thr_err = to_number(combined_env.get("THRESHOLD_ERRORS")) or 0
    
    project = combined_env.get("PROJECT", "design_verification")
    old_version = combined_env.get("OLD_VERSION", "N/A")
    new_version = combined_env.get("NEW_VERSION", "N/A")
    testcases_count = to_number(combined_env.get("TESTCASES_COUNT"))
    
    # ========================================================================
    # STEP 5: PASS/FAIL DECISION (USES SPECIFIC METRICS)
    # ========================================================================
    # Only latency_ms and error_count affect pass/fail
    # Other metrics are informational only
    # ========================================================================
    
    lat = metrics.get("latency_ms")
    err = metrics.get("error_count")
    
    passed, messages = decide(lat, err, thr_lat, thr_err)
    generated_at = datetime.datetime.now().isoformat()
    
    # ========================================================================
    # STEP 6: LOAD DISPLAY NAMES FROM MONITOR.PY
    # ========================================================================
    # Display names are defined in monitor.py and passed via METRIC_DISPLAY_NAMES
    # This ensures export_report.py has ZERO hardcoded metric names
    # Fallback: auto-generate display name from metric_name if not provided
    # ========================================================================
    
    display_names_json = combined_env.get("METRIC_DISPLAY_NAMES", "{}")
    try:
        display_names = json.loads(display_names_json)
    except:
        display_names = {}
    
    # Load metric types from monitor.py
    metric_types_json = combined_env.get("METRIC_TYPES", "{}")
    try:
        metric_types = json.loads(metric_types_json)
    except:
        metric_types = {}
    
    # Load metric evaluation directions from monitor.py
    metric_evaluation_json = combined_env.get("METRIC_EVALUATION", "{}")
    try:
        metric_evaluation = json.loads(metric_evaluation_json)
    except:
        metric_evaluation = {}
    
    # Load testcase details from CSV file (generated by monitor.py)
    testcase_details = _load_testcase_details_csv()
    
    # Build all_metrics list from discovered metrics (in discovery order)
    # ALL metrics are treated equally - no special cases
    all_metrics = []
    for metric_name in metric_order:
        # Get display name from monitor.py, or auto-generate
        display_name = display_names.get(metric_name, metric_name.replace("_", " ").title())
        all_metrics.append((metric_name, display_name))
    
    # Add any old-only metrics not yet in all_metrics
    for old_metric_name in old_metrics.keys():
        if old_metric_name not in metric_order:
            display_name = display_names.get(old_metric_name, old_metric_name.replace("_", " ").title())
            all_metrics.append((old_metric_name, display_name))
    
    # ========================================================================
    # STEP 7: BUILD CONTEXT DICT - PURELY FROM DISCOVERED DATA
    # ========================================================================
    # Context passed to build_markdown_report and build_json_report
    # Contains:
    #  - metrics: {metric_name -> value} for new version
    #  - old_metrics: {metric_name -> value} for old version
    #  - all_metrics: [(metric_name, display_name), ...] for rendering
    # No per-metric assignments (latency, errors, warnings, etc.)
    # ========================================================================
    
    context = {
        "generated_at": generated_at,
        "metrics": metrics,              # {metric_name -> value}
        "old_metrics": old_metrics,      # {metric_name -> value}
        "all_metrics": all_metrics,      # [(metric_name, display_name), ...]
        "metric_types": metric_types,    # {metric_name -> "measured" or "comparison"}
        "metric_evaluation": metric_evaluation,  # {metric_name -> "lower_is_better" or "neutral"}
        "testcase_details": testcase_details,    # {testcase_name -> {latency_ms, errors, vcd}}
        "threshold_latency": thr_lat,
        "threshold_errors": thr_err,
        "passed": bool(passed),
        "messages": messages,
        "project": project,
        "old_version": old_version,
        "new_version": new_version,
        "testcases_count": testcases_count,
        "has_old_version_data": len(old_metrics) > 0,  # Auto-detect version comparison
    }

    if args.format == "md":
        report = build_markdown_report(context)
    else:
        report = build_json_report(context)

    # ========================================================================
    # STEP 8: WRITE REPORT FILE
    # ========================================================================
    # Output location:
    #  - Markdown report: <out_dir>/report-<timestamp>.md
    # Timestamp format: YYYY_MMDD_HHMM_SS_mmm (e.g., 2025_1101_1132_38_706)
    # ========================================================================
    
    ensure_dir(args.out_dir)

    # Format timestamp as YYYY_MMDD_HHMM_SS_mmm (e.g., 2025_1101_2222_35_500)
    dt = datetime.datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
    timestamp = dt.strftime("%Y_%m%d_%H%M_%S") + f"_{dt.microsecond // 1000:03d}"
    default_basename = f"report-{timestamp}"
    if args.out:
        out_path = args.out
    else:
        out_ext = ".md" if args.format == "md" else ".json"
        out_path = os.path.join(args.out_dir, default_basename + out_ext)

    # Write main report file
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Wrote report to {out_path}")


if __name__ == "__main__":
    main()
