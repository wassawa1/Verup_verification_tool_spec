#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================
                   Stage 3: Metrics Extraction
========================================================================
ログファイルからメトリクスを抽出するスクリプト。

カスタマイズポイント:
1. 新しいメトリクスの追加
2. メトリクスの抽出ロジック
3. 閾値の設定

メトリクス追加手順:
1. Metricクラスを継承したクラスを作成
2. extract()メソッドを実装
3. METRICSリストにクラスを追加（インスタンス化不要）

出力形式:
  標準出力に以下を出力:
  - metric_name=value (各メトリクスの値)
  - METRIC_DISPLAY_NAMES=JSON (表示名)
  - METRIC_TYPES=JSON (メトリクスタイプ)
  - METRIC_EVALUATION=JSON (評価方向)
  - METRIC_THRESHOLDS=JSON (閾値)
========================================================================
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
# カスタムメトリクスの定義例
# ============================================================================

class CustomMetric(Metric):
    """
    カスタムメトリクスの実装例
    
    カスタマイズポイント:
    1. __init__: メトリクスの基本情報を設定
       - name: メトリクス名（小文字、アンダースコア区切り）
       - label: 表示名（日本語可）
       - type: MEASURED（測定値）またはCOMPARISON（比較値）
       - direction: LOWER（低いほど良い）、HIGHER（高いほど良い）、NEUTRAL（中立）
       - threshold: 閾値（オプション、MEASUREDタイプのみ）
    
    2. extract: メトリクスの抽出ロジックを実装
       - testcase_name: テストケース名
       - log_dir: ログディレクトリパス
       - log_content: aggregated.logの内容
       - return: 数値
    """
    
    def __init__(self):
        super().__init__(
            name="custom_metric",         # メトリクス名
            label="カスタムメトリクス",      # 表示名
            type=MEASURED,                # 測定値
            direction=LOWER,              # 低いほど良い
            threshold=1000                # 閾値（オプション）
        )
    
    def extract(self, testcase_name, log_dir, log_content):
        """
        メトリクスを抽出
        
        実装例:
        1. ログファイルから値を抽出
        2. ファイルから値を読み込み
        3. 計算して値を生成
        
        Args:
            testcase_name: テストケース名（例: "calculator"）
            log_dir: ログディレクトリ（例: "sim_new"）
            log_content: aggregated.logの内容
            
        Returns:
            数値（int/float）
        """
        # ========================================
        # カスタマイズ: メトリクス抽出ロジック
        # ========================================
        
        # 例1: ログから正規表現で抽出
        # import re
        # for line in log_content.split('\n'):
        #     match = re.match(rf'{testcase_name}:.*?(\d+)\s*units', line)
        #     if match:
        #         return int(match.group(1))
        
        # 例2: ファイルから読み込み
        # metric_file = f"{log_dir}/{testcase_name}.metric"
        # if os.path.exists(metric_file):
        #     with open(metric_file) as f:
        #         return float(f.read().strip())
        
        # 例3: 計算で生成
        # return len(testcase_name) * 100
        
        # デフォルト
        return 0


# ============================================================================
# メトリクスリスト
# ============================================================================
# 
# メトリクス追加方法:
# 1. 上記のようにMetricクラスを継承したクラスを作成
# 2. このリストにクラスを追加（インスタンス化不要！）
# 
# 注意事項:
# - MEASURED（測定値）: 単独で評価できる値（レイテンシ、エラー数など）
# - COMPARISON（比較値）: 新旧を比較して評価する値（波形一致性など）
# - 閾値はMEASUREDタイプのみ設定可能
# - COMPARISONタイプは旧バージョンでは計算されない
# 
# ============================================================================

METRICS = [
    # ========================================
    # フレームワーク提供の基本メトリクス
    # ========================================
    LatencyMetric,        # レイテンシ (ms)
    ErrorCountMetric,     # エラー数
    
    # ========================================
    # カスタムメトリクスをここに追加
    # ========================================
    # CustomMetric,       # カスタムメトリクス例
    
    # 追加例:
    # - WarningCountMetric  # 警告数
    # - MemoryUsageMetric   # メモリ使用量
    # - CoverageMetric      # コードカバレッジ
    # - PerformanceMetric   # パフォーマンス指標
]


def main():
    """
    メイン処理
    
    処理フロー:
    1. aggregated.logを読み込み
    2. 各メトリクスのextract()を呼び出し
    3. 結果を標準出力に出力
    4. CSV形式でtmp/verification_metrics.csvに保存
    
    カスタマイズ不要:
    - このmain()は編集不要
    - METRICSリストにメトリクスを追加するだけ
    """
    process_metrics(METRICS)


if __name__ == "__main__":
    main()
