# Python 検証サンプル

Python バージョンアップグレード（3.9 → 3.14）の検証実装例。

## 概要

このディレクトリには、Pythonバージョンアップグレード時のパフォーマンスとエラーを検証するための完全な実装が含まれています。

## 特徴

- **環境管理**: uv による自動Python環境構築（Ubuntu/GitHub Actions対応）
- **テストケース**: 3個のPythonスクリプト（軽量・重量処理）
- **メトリクス**: レイテンシ、エラー、メモリ使用量

## テストケース

```
testcases/
├── calculator.py         # 計算機（軽量）
├── matrix_operations.py  # 行列演算（重量、10秒級）
└── string_utils.py       # 文字列処理（軽量）
```

### matrix_operations.py の内容
- 素数計算（Sieve of Eratosthenes, 1M）
- 300x300行列積（O(n³)）
- フィボナッチ数列計算
- 実行時間: Python 3.9: ~3.4s, Python 3.14: ~2.0s (38%高速化)

## 使い方

```bash
# このサンプルをセットアップ
make setup-python

# 実行
python3 run_pipeline.py
```

## 環境構築

### uvの自動インストール
`envs.py`が自動的にuvをインストールします（Ubuntu環境）:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Python環境の自動構築
```bash
uv python install 3.9
uv python install 3.14
```

## カスタマイズポイント

### settings.json
```json
{
  "project": "python-test-suite",
  "old_version": "3.9",
  "new_version": "3.14"
}
```

### driver.py
- テストコマンドの変更
- メモリ監視の調整
- タイムアウト設定

### monitor.py
- メモリ抽出ロジック
- カスタムメトリクスの追加

## メトリクス

| メトリクス | 説明 | 閾値 |
|:---|:---|:---|
| レイテンシ (ms) | テスト実行時間 | 2000 ms |
| エラー数 | 実行エラー | 0 |
| メモリ使用量 (KB) | 最大メモリ使用量 | 参考値 |

## 依存関係

- Python 3.x
- uv (自動インストール)
- psutil (オプション: メモリ監視用)

## 参考資料

- [uv公式](https://astral.sh/uv)
- [Python 3.14リリースノート](https://docs.python.org/3.14/whatsnew/3.14.html)
