# Template Scripts

このディレクトリには、新しいプロジェクトを開始するためのテンプレートスクリプトが含まれています。

## 📁 ファイル構成

```
template/scripts/
├── settings.json   # プロジェクト設定
├── envs.py        # Stage 1: 環境構築
├── driver.py      # Stage 2: テスト実行
├── monitor.py     # Stage 3: メトリクス抽出
└── scoreboard.py  # Stage 4: 判定
```

## 🚀 使い方

### 1. テンプレートをコピー

```bash
cp -r template/scripts scripts
```

### 2. カスタマイズ

#### `settings.json`
```json
{
  "project": "your-project-name",
  "old_version": "1.0.0",
  "new_version": "2.0.0"
}
```

#### `driver.py`
- `find_testcases()`: ファイル拡張子を変更（`.py`, `.cpp`, `.v`など）
- `execute_testcase()`: テスト実行コマンドを実装

#### `monitor.py`
- カスタムメトリクスを追加:
  1. `Metric`クラスを継承
  2. `extract()`メソッドを実装
  3. `METRICS`リストに追加

#### `scoreboard.py`
- `get_thresholds()`: 閾値を設定

### 3. 実行

```bash
python3 run_pipeline.py
```

## 📝 各ファイルの役割

### `settings.json`
プロジェクト名、バージョン情報を定義。

### `envs.py`
環境変数とディレクトリを設定。

**カスタマイズポイント:**
- プロジェクト固有の環境変数
- 追加ディレクトリ

### `driver.py`
テストを実行し、ログを生成。

**カスタマイズポイント:**
- テストケースのファイル拡張子（`*.py`, `*.v`, `*.cpp`など）
- コンパイルコマンド
- 実行コマンド
- タイムアウト設定

**実装例:**
```python
# Python実行
proc = subprocess.run(['python3', testcase_file])

# Verilog（Icarus Verilog）
subprocess.run(['iverilog', '-o', vvp_file, testcase_file])
subprocess.run(['vvp', vvp_file])

# C++
subprocess.run(['g++', '-o', exe_file, testcase_file])
subprocess.run([exe_file])
```

### `monitor.py`
ログからメトリクスを抽出。

**カスタマイズポイント:**
- カスタムメトリクスの追加

**メトリクス追加手順:**
```python
class MyMetric(Metric):
    def __init__(self):
        super().__init__(
            name="my_metric",
            label="マイメトリクス",
            type=MEASURED,
            direction=LOWER,
            threshold=1000
        )
    
    def extract(self, testcase_name, log_dir, log_content):
        # 抽出ロジック
        return value

# METRICSリストに追加
METRICS = [
    LatencyMetric,
    ErrorCountMetric,
    MyMetric,  # <- 追加
]
```

### `scoreboard.py`
メトリクスを評価してPass/Fail判定。

**カスタマイズポイント:**
- 閾値の設定
- 評価ロジック
- 総合判定ルール

## 🎯 実装例

### Python版
`examples/python/` を参照:
- Python 3.9 vs 3.14の比較
- メモリ使用量の測定

### Verilog版
`examples/iverilog/` を参照:
- Icarus Verilogでのシミュレーション
- VCD波形解析

## 💡 Tips

### デバッグモード
各スクリプトに`print(..., file=sys.stderr)`でデバッグ出力を追加できます。

### エラーハンドリング
```python
try:
    # 処理
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

### タイムアウト設定
```python
subprocess.run(cmd, timeout=60)  # 60秒でタイムアウト
```

## 🔗 関連ドキュメント

- メインREADME: `../README.md`
- Python実装例: `../examples/python/`
- Verilog実装例: `../examples/iverilog/`
