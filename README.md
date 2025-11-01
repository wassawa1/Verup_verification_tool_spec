# Version Upgrade Verification Pipeline

汎用的なバージョンアップグレード検証パイプライン。旧バージョンと新バージョンでテストを実行し、結果を比較します。

## 🎯 概要

このプロジェクトは、**任意のツール・言語のバージョンアップグレードを検証できる**、汎用的な検証パイプラインテンプレートです。

- **ツール非依存**: Python、C++コンパイラ、Javaランタイム、任意のコマンドラインツールに対応可能
- **バージョン比較**: 旧バージョンと新バージョンで同じテストを実行し、結果を比較
- **モジュール構造**: `scripts/driver.py` をあなたのツール用に書き替えるだけ
- **複数テストケース対応**: テストケースを自動収集・統合実行
- **統合レポート**: 比較結果を 1 つのレポートに自動生成

### 📝 現在の例：Pythonバージョン比較

デフォルトでは、**Python 3.9 vs Python 3.11** のバージョン比較の例を提供しています：

- `testcases/calculator.py` - 計算機の基本機能テスト
- `testcases/string_utils.py` - 文字列操作の基本機能テスト

これらのテストを**旧Python（3.9）と新Python（3.11）で実行**し、パフォーマンスとエラーを比較します。

### このテンプレートがあなたにできること

✅ `testcases/` にテストスクリプト（`.py`, `.cpp`, `.java` など）を配置
✅ `scripts/driver.py` をあなたのツール用にカスタマイズ（C++コンパイラ、etc.）
✅ `settings.json` で旧バージョン・新バージョンを指定
✅ `python run_pipeline.py` で両バージョンのテストを実行・比較
✅ `reports/` に比較レポートが自動生成される

## 🚀 クイックスタート

### 1. Pythonバージョン比較の例（デフォルト）

```bash
# Python 3.9 と 3.11 が両方インストールされている場合
python run_pipeline.py
```

システムに両方のバージョンがない場合は、現在のPythonで両方を実行します（警告が表示されます）。

### 2. 他のツールへの置き換え例

#### C++コンパイラのバージョン比較

`scripts/driver.py` を編集：
python scripts/validate.py
```

✅ 設定ファイルの妥当性チェック
✅ テストケースの存在確認
✅ シミュレーションツールの確認

---

### 5分で動かす最小実装

#### Step 0: プロジェクト設定

**編集ファイル**: `scripts/settings.json`

```json
{
  "project": "my_hardware_project",
  "old_version": "1.0.0",
  "new_version": "2.0.0",
  "simulation_tool": "iverilog",
  "debug_mode": false,
  "dry_run": false
}
```

**設定項目の説明**:
- `simulation_tool`: 使用するツール（`iverilog` / `vivado` / `modelsim`）
- `debug_mode`: `true` で詳細ログ出力
- `dry_run`: `true` でコマンドを実行せずプリント（ツールがない環境でのテスト用）
```

> 💡 **ヒント**: バージョン比較を行う場合は、ここで新旧バージョンを指定します。

---

#### Step 1: `scripts/driver.py` の設定（簡単！）

**朗報**: `settings.json` で `simulation_tool` を指定するだけで、自動的にツールが選択されます！

**対応ツール**:
- ✅ `iverilog` - Icarus Verilog（デフォルト）
- ✅ `vivado` - Xilinx Vivado
- ✅ `modelsim` - Mentor ModelSim

**カスタムツールの場合**:
`scripts/driver.py` の `run_simulation()` 関数を編集してください（詳細なコメント付き）

#### Step 2: `scripts/monitor.py` を確認

**確認箇所**: `METRICS` リスト（約430行目）

デフォルトで以下のメトリクスが定義されています：
```python
METRICS = [
    ("latency_ms",    "レイテンシ (ms)", MEASURED, LOWER),
    ("error_count",   "エラー数",        MEASURED, LOWER),
    # ... その他
]
```

**最初は編集不要**。動作確認後にカスタムメトリクスを追加できます。

---

#### Step 3: 動作確認

```bash
# パイプライン実行
python run_pipeline.py

# レポート確認
cat reports/report-*.md
```

成功すれば、`reports/` にMarkdownレポートが生成されます！

### 段階的なカスタマイズ

#### 🥉 Bronze（最小実装）
- ✅ Step 1-3を完了
- ✅ レイテンシとエラー数のみ測定

#### 🥈 Silver（基本実装）
- ✅ VCD波形ファイル生成を追加
- ✅ `scripts/monitor.py` で波形解析を有効化

```python
# driver.py で VCD 生成を追加
subprocess.run(['iverilog', '-o', 'output.vvp', testcase_file])
subprocess.run(['vvp', 'output.vvp', '-vcd', f'{output_dir}/{testcase_name}.vcd'])
```

#### 🥇 Gold（完全実装）
- ✅ カスタムメトリクスを追加
- ✅ `scripts/user_tools/vcd_utils.py` をカスタマイズ
- ✅ 独自の判定ロジックを実装

```python
# monitor.py の METRICS に追加
METRICS = [
    # ... 既存のメトリクス
    ("test_coverage", "カバレッジ (%)", MEASURED, HIGHER),
]

# _extract_testcase_metrics() に抽出ロジックを追加
def _extract_testcase_metrics(testcase_name, log_dir, log_content):
    metrics = {}
    # ... 既存のコード
    
    # カスタムメトリクス追加
    coverage_file = f"{log_dir}/{testcase_name}.coverage"
    if os.path.exists(coverage_file):
        metrics["test_coverage"] = extract_coverage(coverage_file)
    
    return metrics
```

## �📊 テストケース

パイプラインは `testcases/` ディレクトリ内のすべてのファイルを処理対象とします。

### テストケースの追加方法

`testcases/` ディレクトリに設計ファイルを配置するだけで、パイプラインが自動的に検証の対象に含めます：

```bash
# テストケースを追加
cp my_design.v testcases/
cp my_design.sv testcases/
cp my_design.vhdl testcases/

# パイプライン実行（新しいテストケースが自動的に処理されます）
python run_pipeline.py
```

**ファイル形式**: 
- Verilog/SystemVerilog（`.v`, `.sv`）
- VHDL（`.vhdl`, `.vhd`）
- その他のハードウェア記述言語
- あなたのツールが処理できるファイル形式なら何でも対応可能

詳細は `testcases/README.md` を参照してください。

## 🔄 パイプラインアーキテクチャ

パイプラインは4つのステージから構成され、各ステージは独立したスクリプトで実装されています。

```
┌─────────────────────────────────────────────────────────────────┐
│                    run_pipeline.py (オーケストレーター)          │
└─────────────────────────────────────────────────────────────────┘
         │
         ├─ Stage 1: Environment Setup
         │    └─ scripts/envs.py
         │         - プロジェクト設定（名前、バージョン）
         │
         ├─ Stage 2: Verification Execution
         │    └─ scripts/driver.py
         │         - テストケース実行
         │         - ログ生成（aggregated.log）
         │         - VCDファイル生成（*.vcd）
         │
         ├─ Stage 3: Metrics Extraction
         │    └─ scripts/monitor.py
         │         - ログ解析
         │         - VCD解析 ← tools/vcd_utils.py を使用
         │         - メトリクス計算・正規化
         │         - テストケース詳細CSV生成
         │
         └─ Stage 4: Validation & Reporting
              ├─ scripts/scoreboard.py
              │    - 閾値判定
              │    - Pass/Fail判定
              │
              └─ tools/export_report.py
                   - レポート生成（Markdown/JSON）
                   - テストケース詳細CSV読み込み
```

### 📁 ディレクトリ構成

```
sandbox2/
├── scripts/              # ⚙️ ユーザーカスタマイズ領域
│   ├── envs.py          # Stage 1: 環境設定
│   ├── driver.py        # Stage 2: テストケース実行（ツール依存）
│   ├── monitor.py       # Stage 3: メトリクス抽出（ツール依存）
│   ├── scoreboard.py    # Stage 4: 判定（プロジェクト依存）
│   └── user_tools/      # ⚙️ ユーザーカスタマイズツール
│       └── vcd_utils.py # VCD解析ライブラリ（カスタマイズ可能）
│           ├── parse_vcd()           - VCDパーサー
│           ├── compare_vcd()         - VCD比較
│           ├── count_vcd_signals()   - 信号数カウント
│           ├── count_vcd_lines()     - 行数カウント
│           ├── calculate_vcd_similarity() - 類似度計算
│           └── find_all_vcd_files()  - VCDファイル検索
│
├── tools/               # 🔧 フレームワーク提供部品（編集不要）
│   └── export_report.py # レポート生成エンジン
│       ├── CSV読み込み
│       ├── 動的メトリクス発見
│       └── Markdown/JSON出力
│
├── testcases/           # テストケース（自動収集）
│   ├── adder.v
│   ├── counter.v
│   ├── fsm.v
│   ├── mem.v
│   └── mux.v
│
├── tmp/                 # 中間ファイル
│   ├── testcase_details.csv  # テストケース別詳細（monitor.py生成）
│   └── stage4_env.txt        # Stage 4環境変数
│
├── reports/             # 生成レポート
│   ├── report-*.md      # Markdownレポート
│   └── logs/            # ログファイル
│
├── sim_new/             # 新バージョン実行結果
│   ├── aggregated.log   # 統合ログ（driver.py生成）
│   └── *.vcd            # 波形ファイル
│
└── sim_old/             # 旧バージョン実行結果（比較用）
    ├── aggregated.log
    └── *.vcd
```

### 🔗 依存関係マップ

```
scripts/monitor.py (Stage 3)
    ↓ import
scripts/user_tools/vcd_utils.py
    - parse_vcd()
    - compare_vcd()
    - count_vcd_signals()
    - count_vcd_lines()
    - calculate_vcd_similarity()
    - find_all_vcd_files()

scripts/monitor.py (Stage 3)
    ↓ 生成
tmp/testcase_details.csv
    ↓ 読み込み
tools/export_report.py (Stage 4)
```

**設計原則**:
- `scripts/` = ⚙️ **ユーザーカスタマイズ領域**（プロジェクト・ツール依存）
  - パイプライン制御スクリプト（Stage 1-4）
  - あなたのツール（Vivado, ModelSim等）に合わせて実装
  
- `scripts/user_tools/` = ⚙️ **ユーザーカスタマイズツール**
  - VCD解析ロジックなど、カスタマイズ可能なユーティリティ
  - 独自フォーマット対応、特定信号抽出など自由に編集
  
- `tools/` = 🔧 **フレームワーク提供部品**（汎用、編集不要）
  - メトリクス動的発見・レポート生成
  - プロジェクト非依存の汎用処理

**ユーザーが編集するファイル**:
- ✅ `scripts/envs.py` - プロジェクト設定
- ✅ `scripts/driver.py` - テストケース実行ロジック
- ✅ `scripts/monitor.py` - メトリクス抽出ロジック
- ✅ `scripts/scoreboard.py` - 判定基準
- ✅ `scripts/user_tools/vcd_utils.py` - VCD解析カスタマイズ

**ユーザーが編集しないファイル**:
- 🔧 `tools/export_report.py` - フレームワーク提供
- 🔧 `run_pipeline.py` - フレームワーク提供

---

## 📝 各スクリプトの編集ガイド

### `scripts/driver.py` - Stage 2（最重要）

**役割**: あなたの検証ツールを呼び出す

**🎉 朗報**: `settings.json` の `simulation_tool` を変更するだけで、Icarus Verilog / Vivado / ModelSim に自動対応！

**対応済みツール**:
```json
{
  "simulation_tool": "iverilog"  // または "vivado", "modelsim"
}
```

**カスタムツールの場合のみ編集が必要**:
- 編集箇所: `run_simulation()` 関数（約40行目）
- 詳細なコメントとサンプルコードが含まれています
- 未知のツール名を指定すると、エラーメッセージで次のステップを案内

**デバッグ機能**:
```json
{
  "debug_mode": true,   // 詳細ログ出力
  "dry_run": true       // コマンドをプリントのみ（実行しない）
}
```

---

### `scripts/monitor.py` - Stage 3

**役割**: ログファイルからメトリクスを抽出

**🎯 新しい設計: メトリクスクラスベース**

メトリクスの定義と抽出ロジックが**一体化**しています！

**基本的な使い方**:
1. `Metric`クラスを継承
2. `extract()`メソッドを実装
3. `METRICS`リストにクラスを追加（**インスタンス化不要！**）

**メトリクス追加例**:

<details>
<summary><b>カバレッジメトリクスの追加</b></summary>

```python
# Step 1: Metric クラスを継承
class CoverageMetric(Metric):
    def __init__(self):
        super().__init__(
            name="test_coverage",
            label="カバレッジ (%)",
            type=MEASURED,
            direction=HIGHER  # 高いほど良い
        )
    
    def extract(self, testcase_name, log_dir, log_content):
        """カバレッジファイルから抽出"""
        coverage_file = f"{log_dir}/{testcase_name}.coverage"
        if os.path.exists(coverage_file):
            with open(coverage_file) as f:
                return float(f.read().strip())
        return 0.0

# Step 2: METRICS リストに追加（()不要！）
METRICS = [
    LatencyMetric,        # 既存
    ErrorCountMetric,     # 既存
    CoverageMetric,       # ← 追加！()不要！
]
```

</details>

<details>
<summary><b>メモリ使用量メトリクスの追加</b></summary>

```python
class MemoryUsageMetric(Metric):
    def __init__(self):
        super().__init__(
            name="memory_mb",
            label="メモリ使用量 (MB)",
            type=MEASURED,
            direction=LOWER  # 低いほど良い
        )
    
    def extract(self, testcase_name, log_dir, log_content):
        """ログからメモリ使用量を抽出"""
        for line in log_content.split('\n'):
            if f"{testcase_name}:" in line and "memory" in line.lower():
                match = re.search(r'(\d+)\s*MB', line)
                if match:
                    return int(match.group(1))
        return 0

# METRICS に追加（シンプル！）
METRICS = [
    # ... 既存のメトリクス
    MemoryUsageMetric,  # ← ()不要！
]
```

</details>

**✅ 自動で反映される**:
- CSV出力に追加
- レポートに表示
- テストケース別詳細に含まれる

**💡 メリット**:
- **()不要** - クラス名だけで追加できる
- メトリクス定義と抽出ロジックが1箇所
- IDEの補完が効く
- 型安全
- パターンが明確で真似しやすい

---

### `scripts/scoreboard.py` - Stage 4

**役割**: 合格/不合格の判定基準

**編集箇所**: 閾値の定数（10-15行目付近）

```python
THRESHOLD_LATENCY = 2000  # ms（ミリ秒）
THRESHOLD_ERRORS = 0      # エラー数
```

**カスタム判定ロジック**:
```python
def decide(lat, err, thr_lat, thr_err):
    ok = True
    messages = []
    
    # あなたの判定ロジック
    if lat > thr_lat:
        messages.append(f"レイテンシ超過: {lat} > {thr_lat}")
        ok = False
    
    if err > thr_err:
        messages.append(f"エラー検出: {err}件")
        ok = False
    
    return ok, messages
```

---

### `scripts/envs.py` - Stage 1

**役割**: プロジェクト情報の設定

**編集箇所**: `scripts/settings.json`

```json
{
  "project": "my_hardware_project",
  "old_version": "1.0.0",
  "new_version": "2.0.0"
}
```

**編集頻度**: 低（プロジェクト開始時、バージョン更新時のみ）

> 💡 **ヒント**: `envs.py`は自動で`settings.json`を読み込みます。`settings.json`を編集するだけでOKです。

---

### `scripts/user_tools/vcd_utils.py` - VCD解析

**役割**: VCD波形ファイルの解析（カスタマイズ可能）

**編集例**:

```python
# 特定の信号だけを抽出
def count_specific_signals(vcd_file, signal_pattern):
    signals, _ = parse_vcd(vcd_file)
    matched = [s for s in signals.values() if signal_pattern in s]
    return len(matched)

# クロック周波数を計算
def calculate_clock_frequency(vcd_file, clock_signal_name):
    signals, changes = parse_vcd(vcd_file)
    # あなたのロジック
    return frequency
```

**使用方法**:
```python
# monitor.py から使用
from user_tools.vcd_utils import count_specific_signals

metrics["clock_signals"] = count_specific_signals(vcd_path, "clk")
```


### 4段階処理フロー

```
Stage 1: Environment Setup
  └─ バージョン情報・環境変数設定

Stage 2: Verification Execution
  └─ テストケース処理
     • 設計ファイルのコンパイル
     • シミュレーション実行
     • 波形（VCD）ファイル生成

Stage 3: Metrics Extraction
  └─ メトリクス収集・正規化
     • 実行時間
     • エラー・警告カウント
     • 波形データ分析
     ほか

Stage 4: Validation & Reporting
  └─ レポート生成
```

各ステージは独立しており、カスタマイズが容易な設計になっています。

## 📋 生成メトリクス

パイプラインは複数のメトリクスを自動抽出・統合します：

### 判定対象の指標
- 実行時間（レイテンシ）
- エラーカウント

### 参考指標
- 警告カウント
- ファイルサイズ
- 波形データ統計
- その他設計ツール固有のメトリクス

メトリクスは設計ツールに応じてカスタマイズ可能です。

## 📄 生成レポート

パイプラインは検証結果を構造化されたレポートとして出力します。

レポートは以下のセクションから構成されます：
- 検証結果の総括（合格/不合格判定）
- テスト環境情報
- メトリクス表示
- 結論と詳細メッセージ
- メタ情報（実行日時など）

レポート形式はカスタマイズ可能で、デフォルトは Markdown です。

## 🚀 使用方法

### ローカル実行

```bash
python run_pipeline.py
```

### 環境変数でカスタマイズ

```bash
PROJECT=my-project THRESHOLD_LATENCY=3000 python run_pipeline.py
```

### GitHub Actions実行

リポジトリに push すると、`.github/workflows/` に定義されたワークフローが自動実行されます。

### ローカルでのワークフロー事前テスト

GitHub Actions ワークフローをローカルでテスト実行できます（`act` が必要）。

## 📁 ディレクトリ構成

```
.
├── README.md                    # このドキュメント
├── run_pipeline.py              # パイプラインメインランナー
│
├── scripts/                     # 【ここを書き替える】
│   ├── envs.py                  # Stage 1: プロジェクト設定・環境変数 ⭐
│   ├── driver.py                # Stage 2: あなたのツールに合わせて実装 ⭐
│   ├── monitor.py               # Stage 3: ツールのログ形式に合わせて実装 ⭐
│   └── scoreboard.py            # Stage 4: 検証ルール設定 ⭐
│
├── tools/
│   └── export_report.py         # レポート生成 (通常変更不要)
│
├── testcases/                   # テストケース配置ディレクトリ
│   └── README.md                # テストケース説明書
│
├── .github/workflows/
│   └── version-upgrade.yml      # GitHub Actions定義
│
└── reports/                     # 実行結果出力先
    ├── report-*.md              # レポートファイル
    └── logs/
```

**⭐ あなたが書き替える必要があるファイル（全 4 ファイル）**:
- `scripts/envs.py`: プロジェクト設定・環境変数
- `scripts/driver.py`: コンパイル・シミュレーション実行
- `scripts/monitor.py`: ログ解析・メトリクス抽出
- `scripts/scoreboard.py`: 検証ルール設定

## 🎯 設計上の特徴

### モジュール化された構造

各ステージ（Stage 1-4）は独立しており、カスタマイズや置き換えが容易です。

### 環境変数による制御

パイプラインの動作は環境変数で柔軟に制御できます。

## 🔧 カスタマイズガイド

### パイプラインの構造

パイプラインは 4 つの独立したステージで構成されており、各ステージは完全にカスタマイズ可能です：

```
scripts/
├── envs.py        (Stage 1) ← 【ここを書き替える】プロジェクト設定・環境変数
├── driver.py      (Stage 2) ← 【ここを書き替える】設計ツール用に実装
├── monitor.py     (Stage 3) ← 【ここを書き替える】ログ解析をカスタマイズ
└── scoreboard.py  (Stage 4) ← 【ここを書き替える】検証ルールを定義
```

### Stage 1 (envs.py) - プロジェクト設定

**目的**: プロジェクト固有の設定（プロジェクト名、バージョン、その他環境変数）を定義

**あなたのツール用に書き替える部分**:
- プロジェクト名
- バージョン情報
- その他のプロジェクト固有の環境変数
- ツール固有の設定値

**インタフェース**:
```python
# 標準出力に key=value 形式で出力
print(f"project={プロジェクト名}")
print(f"version={バージョン}")
# その他の設定値...
```

### Stage 2 (driver.py) - テスト実行ドライバ

**目的**: テストケースをコンパイル・シミュレーションし、メトリクスを抽出

**あなたのツール用に書き替える部分**:
- コンパイルコマンド（例：`iverilog` → `vlog` / `vhdl` など）
- シミュレーションコマンド（例：`vvp` → `vsim` / `xsim` など）
- ログ出力先
- VCD生成の有無・形式

**インタフェース**:
```python
# 標準出力に key=value 形式で出力
print(f"latency={実行時間}")
print(f"errors={エラー数}")
print(f"testcases_count={処理したテストケース数}")
```

### Stage 3 (monitor.py) - メトリクス抽出

**目的**: Stage 2 の出力ログをパースして、メトリクスを抽出・正規化

**あなたのツール用に書き替える部分**:
- ログファイルパスの検出
- ログ形式のパース（正規表現やテキスト検索）
- 実行時間の抽出方法
- エラー・警告のカウント方法
- VCD ファイルの解析（必要に応じて）

**インタフェース**:
```python
# 標準出力に key=value 形式で出力
print(f"latency_ms={値}")
print(f"error_count={値}")
print(f"warning_count={値}")
# その他メトリクス...
```

### Stage 4 (scoreboard.py) - 検証ルール設定

**目的**: 検証結果の判定ルール（閾値、合格条件など）を定義

**あなたのツール用に書き替える部分**:
- レイテンシ閾値
- エラー許容数
- その他の検証ルール
- 合格/不合格の判定ロジック

## ✅ カスタマイズの流れ

1. **テストケース配置**: `testcases/` に設計ファイルを配置
2. **Stage 1 実装**: `scripts/envs.py` をあなたのプロジェクト設定に合わせて実装
   - プロジェクト名を設定
   - バージョン情報を設定
   - その他の環境変数を設定
3. **Stage 2 実装**: `scripts/driver.py` をあなたのツールに合わせて実装
   - コンパイルコマンドを指定
   - シミュレーションコマンドを指定
   - メトリクス出力形式を統一
4. **Stage 3 実装**: `scripts/monitor.py` をログ形式に合わせて実装
   - ログパースロジック実装
   - メトリクス正規化実装
5. **Stage 4 実装**: `scripts/scoreboard.py` を検証ルールに合わせて実装
   - 閾値設定
   - 判定ロジック実装
6. **実行**: `python run_pipeline.py`

詳細な実装例は各 `scripts/` ファイルのコメントを参照してください。

## ✅ 動作確認済み

- ✅ ローカル実行（複数OS）
- ✅ GitHub Actions実行
- ✅ 複数テストケース統合実行
- ✅ レポート生成
- ✅ 複数ツール対応設計

## 🔧 技術スタック

### ツール対応
このテンプレートは **あらゆるハードウェア設計ツール** に対応するよう設計されています。

- Verilog/SystemVerilog シミュレータなら、どれでも使用可能
- `scripts/driver.py` と `scripts/monitor.py` をあなたのツール用に実装するだけ
- 具体例：Icarus Verilog、Vivado、Questasim、VCS、ModelSim、その他すべてのEDAツール

### 言語・フレームワーク
- **Python 3.14.0**: パイプライン実装言語
- **Verilog/SystemVerilog**: ハードウェア記述言語
- **GitHub Actions**: CI/CD自動化
- **act**: GitHub Actions ローカルシミュレータ

### OS対応
- Windows (PowerShell)
- WSL (Windows Subsystem for Linux)
- Ubuntu / Linux
- macOS

## 📝 ライセンス

このプロジェクトはサンドボックス環境用です。

---

**最終更新**: 2025年11月1日
