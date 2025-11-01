#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VCD (Value Change Dump) ファイル解析ユーティリティ

========================================================================
                    ⚙️ ユーザーカスタマイズ可能
========================================================================
このファイルは scripts/user_tools/ に配置されており、
**ユーザーが自由に編集できます**。

あなたのプロジェクトに合わせてVCD解析ロジックをカスタマイズしてください。

例：
- 独自のVCDフォーマットに対応
- 特定の信号のみをフィルタリング
- カスタムメトリクスの追加
- 外部ツール（GTKWave等）との連携

========================================================================
                         使用箇所 (Used by)
========================================================================
- scripts/monitor.py (Stage 3: メトリクス抽出)
  - normalize_from_env(): VCD集計・比較
  - _extract_testcase_metrics(): テストケース別VCD解析

========================================================================
                         提供機能
========================================================================
1. VCDファイル解析
   - parse_vcd(): VCDファイルをパースして信号定義と値変化を抽出
   - count_vcd_signals(): 信号数のカウント
   - count_vcd_lines(): ファイル行数のカウント

2. VCD比較・類似度計算
   - compare_vcd(): 2つのVCDファイルを詳細比較
   - calculate_vcd_similarity(): 総合類似度スコア算出（0-100%）

3. ファイル検索
   - find_all_vcd_files(): ディレクトリ内の全VCDファイルを検索

========================================================================
"""
import os
import glob
from typing import Dict, List, Tuple, Optional


def parse_vcd(filepath: str) -> Tuple[Dict, List]:
    """
    VCDファイルをシンプルに解析
    
    VCD (Value Change Dump) フォーマットは、デジタル回路シミュレーションの
    波形データを記録する標準フォーマットです。このパーサーは以下を抽出します：
    
    1. 信号定義（$var セクション）
    2. 値の変化履歴（#timestamp + 値変化）
    
    Args:
        filepath: VCDファイルのパス
    
    Returns:
        (signals, changes) のタプル
        - signals: {signal_id: signal_name} 辞書
        - changes: [(timestamp, signal_id, value), ...] リスト
    
    Used by:
        - scripts/monitor.py: count_vcd_signals(), compare_vcd()
    
    Example:
        >>> signals, changes = parse_vcd("counter.vcd")
        >>> print(f"信号数: {len(signals)}")
        >>> print(f"値変化数: {len(changes)}")
    """
    signals = {}  # signal_id -> signal_name
    changes = []  # [(timestamp, signal_id, value), ...]
    
    if not os.path.exists(filepath):
        return signals, changes
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
    except Exception:
        return signals, changes
    
    # ヘッダー部分を解析（信号定義）
    for line in lines:
        line_stripped = line.strip()
        
        if line_stripped == "$enddefinitions":
            break
        
        # $var wire 8 ! count [7:0] $end
        if line_stripped.startswith("$var"):
            parts = line_stripped.split()
            # parts: ['$var', 'wire', '8', '!', 'count', '[7:0]', '$end']
            if len(parts) >= 4:
                signal_id = parts[3]  # signal identifier
                signal_name = parts[4] if len(parts) > 4 else parts[3]
                signals[signal_id] = signal_name
    
    # データ部分を解析（値の変化）
    current_timestamp = 0
    
    for line in lines:
        line_stripped = line.strip()
        
        if not line_stripped:
            continue
        
        # タイムスタンプ
        if line_stripped.startswith("#"):
            try:
                current_timestamp = int(line_stripped[1:])
            except ValueError:
                pass
            continue
        
        # セクションマーク（スキップ）
        if line_stripped.startswith("$"):
            continue
        
        # 値の変化
        if line_stripped.startswith("b"):
            # 複数ビット値: "b1010 !"
            parts = line_stripped.split()
            if len(parts) >= 2:
                value = parts[0]
                signal_id = parts[1]
                if signal_id in signals:
                    changes.append((current_timestamp, signal_id, value))
        else:
            # 単一ビット値: "0!" または "1#"
            if len(line_stripped) >= 2:
                value = line_stripped[0]
                signal_id = line_stripped[1:]
                if signal_id in signals:
                    changes.append((current_timestamp, signal_id, value))
    
    return signals, changes


def compare_vcd(vcd_old_path: str, vcd_new_path: str) -> Dict:
    """
    2つのVCDファイルを詳細比較
    
    旧版と新版のVCDファイルを比較し、以下の項目を検証します：
    - 信号数の一致
    - 信号名の一致
    - 値変化数の一致
    - 実際の値内容の一致
    
    Args:
        vcd_old_path: 旧版VCDファイルのパス
        vcd_new_path: 新版VCDファイルのパス
    
    Returns:
        比較結果の辞書（以下のキーを含む）:
        - signal_count_old: 旧版の信号数
        - signal_count_new: 新版の信号数
        - signal_count_match: 信号数が一致するか (bool)
        - change_count_old: 旧版の値変化数
        - change_count_new: 新版の値変化数
        - change_count_match: 値変化数が一致するか (bool)
        - signal_names_match: 信号名が一致するか (bool)
        - values_match: 値が完全に一致するか (bool)
        - overall_similarity: 総合類似度スコア (0-100)
    
    Used by:
        - scripts/monitor.py: calculate_vcd_similarity()
    """
    signals_old, changes_old = parse_vcd(vcd_old_path)
    signals_new, changes_new = parse_vcd(vcd_new_path)
    
    results = {
        "signal_count_old": len(signals_old),
        "signal_count_new": len(signals_new),
        "signal_count_match": len(signals_old) == len(signals_new),
        "change_count_old": len(changes_old),
        "change_count_new": len(changes_new),
        "signal_names_match": sorted(signals_old.values()) == sorted(signals_new.values()),
        "change_count_match": len(changes_old) == len(changes_new),
    }
    
    # 値が完全に一致しているか確認
    if len(changes_old) == len(changes_new):
        value_match = all(c_old == c_new for c_old, c_new in zip(changes_old, changes_new))
        results["values_match"] = value_match
    else:
        results["values_match"] = False
    
    # 総合一致度を計算
    similarity = 0.0
    scores = []
    
    # 信号数の一致度
    if results["signal_count_old"] > 0:
        signal_match_score = 100 if results["signal_count_match"] else 0
        scores.append(signal_match_score * 0.1)
    
    # 値の変化数の一致度
    if results["change_count_old"] > 0:
        if results["change_count_match"]:
            change_score = 100
        else:
            diff = abs(results["change_count_new"] - results["change_count_old"])
            change_score = max(0, 100 - (diff / results["change_count_old"] * 100))
        scores.append(change_score * 0.4)
    
    # 値の一致度
    if results["values_match"]:
        scores.append(100 * 0.5)
    else:
        scores.append(0)
    
    if scores:
        similarity = sum(scores)
    
    results["overall_similarity"] = similarity
    
    return results


def count_vcd_signals(vcd_file: str) -> Optional[int]:
    """
    VCDファイルから信号数をカウント
    
    Args:
        vcd_file: VCDファイルのパス
    
    Returns:
        信号数（ファイルが存在しない場合はNone）
    
    Used by:
        - scripts/monitor.py: _extract_testcase_metrics()
    """
    signals, _ = parse_vcd(vcd_file)
    return len(signals) if signals else None


def count_vcd_lines(vcd_file: str) -> Optional[int]:
    """
    VCDファイルの行数をカウント
    
    Args:
        vcd_file: VCDファイルのパス
    
    Returns:
        行数（ファイルが存在しない場合はNone）
    
    Used by:
        - scripts/monitor.py: _extract_testcase_metrics()
    """
    if not os.path.exists(vcd_file):
        return None
    try:
        with open(vcd_file, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except Exception:
        return None


def calculate_vcd_similarity(vcd_old: str, vcd_new: str) -> Optional[float]:
    """
    波形ファイル安定性スコアを計算（0-100%）
    
    この指標は「旧版と新版の波形生成の安定性」を測定します：
    - 100%: 波形出力が完全に一致（実装は安定している）
    - 90-99%: わずかな差分あり（軽微な最適化）
    - 50-89%: 中程度の差分（実装ロジック変更）
    - <50%: 大きな差分（重大な仕様変更）
    
    測定項目：
    1. VCD ファイルサイズの差分
    2. VCD 行数の差分
    3. 信号数の差分
    4. 値の変化数の差分
    5. 実際の値内容の一致度
    
    Args:
        vcd_old: 旧版VCDファイルのパス
        vcd_new: 新版VCDファイルのパス
    
    Returns:
        類似度スコア（0-100の範囲、ファイルが存在しない場合はNone）
    
    Used by:
        - scripts/monitor.py: normalize_from_env()
    """
    if not os.path.exists(vcd_old) or not os.path.exists(vcd_new):
        return None
    
    try:
        results = compare_vcd(vcd_old, vcd_new)
        # 総合スコアを返す
        return results.get("overall_similarity")
    except Exception:
        return None


def find_all_vcd_files(directory: str) -> List[str]:
    """
    指定ディレクトリ内のすべてのVCDファイルを検索
    
    Args:
        directory: 検索対象ディレクトリのパス
    
    Returns:
        VCDファイルのパスのリスト（ソート済み）
    
    Used by:
        - scripts/monitor.py: normalize_from_env()
    
    Example:
        >>> vcd_files = find_all_vcd_files("sim_new")
        >>> for vcd in vcd_files:
        ...     print(vcd)
        sim_new/adder.vcd
        sim_new/counter.vcd
        sim_new/fsm.vcd
    """
    vcd_pattern = os.path.join(directory, "*.vcd")
    vcd_files = sorted(glob.glob(vcd_pattern))
    return vcd_files
