# Verilog 検証サンプル

Icarus Verilog を使用したバージョンアップグレード検証の実装例。

## 概要

このディレクトリには、Verilogハードウェア設計のバージョンアップグレード検証を行うための完全な実装が含まれています。

## 特徴

- **シミュレータ**: Icarus Verilog (iverilog)
- **テストケース**: 5個のVerilogモジュール
- **メトリクス**: レイテンシ、エラー、VCD解析（信号数、波形一致性）

## テストケース

```
testcases/
├── adder.v       # 加算器
├── counter.v     # カウンタ
├── fsm.v         # 有限状態機械
├── mem.v         # メモリ
└── mux.v         # マルチプレクサ
```

## 使い方

```bash
# このサンプルをセットアップ
make setup-iverilog

# 実行
python3 run_pipeline.py
```

## カスタマイズポイント

### driver.py
- シミュレーションツールの変更（Vivado、ModelSimなど）
- VCD出力設定

### monitor.py
- VCD解析ロジックのカスタマイズ
- 独自メトリクスの追加

### user_tools/vcd_utils.py
- VCDパーサーのカスタマイズ
- 特定信号の抽出

## メトリクス

| メトリクス | 説明 | 閾値 |
|:---|:---|:---|
| レイテンシ (ms) | シミュレーション実行時間 | 2000 ms |
| エラー数 | コンパイル・実行エラー | 0 |
| 警告数 | コンパイル警告 | 0 |
| VCD信号数 | 波形に含まれる信号数 | 参考値 |
| VCD行数 | 波形ファイルの行数 | 参考値 |
| VCDサイズ (KB) | 波形ファイルサイズ | 参考値 |
| 波形一致性 | 新旧波形の一致度 | 比較値 |

## 依存関係

- Icarus Verilog (`iverilog`, `vvp`)
- Python 3.x
- psutil (オプション: メモリ監視用)

## 参考資料

- [Icarus Verilog公式](http://iverilog.icarus.com/)
- [VCDファイル形式](https://en.wikipedia.org/wiki/Value_change_dump)
