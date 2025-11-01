# Version Upgrade Verification Pipeline

## 🚀 概要

Version Upgrade Verification Pipeline はツールの **異なるバージョン環境に対して自動テスト・性能比較・結果評価を行う検証パイプライン**。

GitHub Actions や `act` を用いて CI 上で再現可能な形で実行でき、レイテンシ・エラー数・メモリ使用量などの指標を計測し、スコアボードで合否判定する仕組みを備える。

---

## ✅ 特徴

- **バージョン差異の自動検証**（例：Python 3.9 vs 3.14）
- **GitHub Actions / act 対応の CI パイプライン**
- **レイテンシ・メモリ・エラーカウントの自動測定**
- **envs → driver → monitor → scoreboard の構造化フロー**
- **Makefile による簡潔なセットアップと実行**

---

## 📂 ディレクトリ構造

```
├─ examples/        # Python・Verilog のサンプルコード
├─ scripts/         # プロジェクト設定/テスト実行ロジック
│   ├─ settings.json
│   ├─ driver.py    # 入力→実行→ログ取得処理
│   └─ monitor.py   # メトリクス定義（時間・メモリ・エラー等）
├─ testcases/       # テスト入力ファイル
├─ tools/           # CI 実行/補助ツール
├─ run_pipeline.py  # パイプライン一括実行スクリプト
└─ Makefile         # setup と test 実行管理
```

---

## ⚙ 実行方法（ローカル）

### 1. セットアップ
```bash
make setup-python      # Python 環境構築
make setup-iverilog    # Icarus Verilog セットアップ（必要な場合）
```

### 2. テスト実行
```bash
make test              # 全テスト実行
```

### 3. 直接スクリプトで実行する場合
```bash
python run_pipeline.py
```

---

## 🤖 GitHub Actions（CIでの利用例）

`.github/workflows/verify.yml`：

```yaml
name: Version Upgrade Check

on:
  workflow_dispatch:

jobs:
  decide-pass-fail:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make setup-python
      - run: make test
      - uses: actions/upload-artifact@v4
        with:
          name: report
          path: out/report.txt
```

---

## 📊 評価指標（スコアボード）

| 指標        | 例              | FAIL 条件例        |
|-------------|------------------|---------------------|
| レイテンシ  | 150ms → 320ms    | > 1000ms            |
| エラー数    | 0 → 2            | > 0                 |
| メモリ使用  | 120MB → 140MB    | > 150MB             |

※ `scripts/monitor.py` でメトリクス定義、`scoreboard` ロジックで PASS/FAIL 判定。

---

## 📌 使用技術

- **言語**：Python / Verilog  
- **CIツール**：GitHub Actions / nektos/act  
- **設計**：Makefile ベースのパイプライン、JSON 設定ファイル  
- **測定**：時間・メモリ・例外カウント・ログ解析

---

## 📝 今後の拡張候補

- pytest/unittest と統合  
- JUnit XML や HTML レポート生成  
- Slack / GitHub Issues への自動通知  
- Docker コンテナ対応テスト環境  
- 複数言語（TCL/C++）対応

---

## 📖 補足

- ライセンス表記はなし  
- 公開 README 用に内容を凝縮・整形済み  

