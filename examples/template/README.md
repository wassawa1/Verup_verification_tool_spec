# テンプレート

新規プロジェクト用のひな形テンプレート。

## 概要

このディレクトリには、任意のツール・言語のバージョンアップグレード検証を実装するためのひな形が含まれています。充実したコメントと実装例により、スムーズに開始できます。

## 特徴

- **コメント充実**: 各関数に詳細な説明
- **カスタマイズポイント明示**: `========` で区切って明確化
- **複数の実装例**: Python/Verilog/C++の例を記載
- **段階的実装**: TODOコメントで次のステップを明示
- **デフォルト実装**: そのまま動くダミー実装付き

## 使い方

### 1. テンプレートをコピー

```bash
cp -r examples/template/scripts scripts
```

### 2. カスタマイズ

#### settings.json
```json
{
  "project": "your-project-name",
  "old_version": "1.0.0",
  "new_version": "2.0.0"
}
```

#### driver.py
```python
# ファイル拡張子を変更
patterns = ["*.py"]  # <- *.cpp, *.v など

# テスト実行コマンドを実装
def execute_testcase(testcase_file, output_dir):
    # 例: Pythonスクリプト実行
    proc = subprocess.run(['python3', str(testcase_file)])
    
    # 例: Verilogシミュレーション
    # subprocess.run(['iverilog', '-o', vvp_file, testcase_file])
    # subprocess.run(['vvp', vvp_file])
    
    # 例: C++コンパイル・実行
    # subprocess.run(['g++', '-o', exe_file, testcase_file])
    # subprocess.run([exe_file])
```

#### monitor.py
```python
# カスタムメトリクスを追加
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
        # 抽出ロジック実装
        return value

METRICS = [
    LatencyMetric,
    ErrorCountMetric,
    MyMetric,  # <- 追加
]
```

#### scoreboard.py
```python
# 閾値を設定
thresholds = {
    "latency_ms": 2000,
    "error_count": 0,
    "my_metric": 1000,
}
```

### 3. テストケースを追加

```bash
mkdir -p testcases
cp your_test.* testcases/
```

### 4. 実行

```bash
python3 run_pipeline.py
```

## ファイル構成

```
template/scripts/
├── settings.json   # プロジェクト設定
├── envs.py        # Stage 1: 環境構築
├── driver.py      # Stage 2: テスト実行 ⭐最重要
├── monitor.py     # Stage 3: メトリクス抽出
├── scoreboard.py  # Stage 4: 判定
└── README.md      # このファイル
```

## カスタマイズの流れ

1. **settings.json** - プロジェクト名とバージョン
2. **driver.py** - テスト実行ロジック（最重要）
   - ファイル拡張子
   - コンパイルコマンド
   - 実行コマンド
3. **monitor.py** - メトリクス定義
   - カスタムメトリクスの追加
4. **scoreboard.py** - 閾値設定
5. **testcases/** - テストファイル配置

## 実装例の参照

- **Python版**: `examples/python/` - Pythonバージョン比較
- **Verilog版**: `examples/iverilog/` - Verilogシミュレーション

## Tips

### デバッグ出力
```python
print("Debug info", file=sys.stderr)  # 標準エラー出力
```

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

## ヘルプ

詳細は各ファイルのコメントを参照してください。すべてのカスタマイズポイントに `========` で始まるコメントが付いています。
