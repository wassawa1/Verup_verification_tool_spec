# テストケース一覧

このディレクトリには Python テストケースが含まれています。

## テストケース

### 1. calculator.py
- **説明**: 基本的な計算機プログラム
- **機能**: 加減乗除、平方根、べき乗計算
- **処理時間**: 軽量（〜100ms）
- **目的**: 基本的な Python 演算の性能確認

### 2. string_utils.py
- **説明**: 文字列処理ユーティリティ
- **機能**: 大文字変換、反転、パリンドロムチェック
- **処理時間**: 軽量（〜50ms）
- **目的**: 文字列操作の性能確認

### 3. matrix_operations.py
- **説明**: 重い計算処理（性能テスト用）
- **機能**: 
  - 素数計算（Sieve of Eratosthenes, 1M範囲）
  - 300×300行列積（O(n³)アルゴリズム）
  - フィボナッチ数列計算
- **処理時間**: 重量（2〜3秒）
- **目的**: CPU集約的処理での性能差確認
- **期待される改善**: Python 3.14 は 3.9 より約30-40%高速

## パフォーマンス目標

| テストケース | Python 3.9 | Python 3.14 | 改善率 |
|:---|---:|---:|---:|
| calculator | 〜60ms | 〜60ms | 同等 |
| string_utils | 〜40ms | 〜40ms | 同等 |
| matrix_operations | 〜3000ms | 〜1900ms | **約38%改善** |

## 実行方法

```bash
# 個別実行（デバッグ用）
python3 testcases/calculator.py
python3 testcases/matrix_operations.py
python3 testcases/string_utils.py

# パイプライン経由（推奨）
make setup-python
make test
```

## カスタマイズ

新しいテストケースを追加する場合:
1. このディレクトリに `*.py` ファイルを配置
2. 実行可能な Python スクリプトとして実装
3. エラー時は非ゼロの終了コードを返す

例:
```python
#!/usr/bin/env python3
import sys

def test_something():
    # テストロジック
    if error:
        sys.exit(1)  # 失敗
    return True

if __name__ == "__main__":
    test_something()
    print("Test passed")
```
