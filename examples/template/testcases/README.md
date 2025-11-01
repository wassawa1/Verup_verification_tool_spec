# Test Cases

テンプレート用のサンプルテストケース配置ディレクトリ。

## 使い方

このディレクトリは空です。プロジェクトに合わせてテストファイルを配置してください。

```bash
# テストケースを追加
cp your_test_file.* testcases/

# 例: Pythonテスト
cp test_calculator.py testcases/

# 例: Verilogテスト
cp adder.v testcases/

# 例: C++テスト
cp matrix_test.cpp testcases/
```

## 対応ファイル形式

`driver.py` で設定したファイル拡張子に応じて自動検出されます:

- **Python**: `*.py`
- **Verilog/SystemVerilog**: `*.v`, `*.sv`
- **VHDL**: `*.vhd`, `*.vhdl`
- **C/C++**: `*.c`, `*.cpp`
- **その他**: 任意の形式に対応可能

## テストケースの要件

- ファイル名がテストケース名になります
- `driver.py` で定義した実行コマンドで実行可能であること
- エラー発生時は非ゼロの終了コードを返すこと（推奨）

## 参考

実装例のテストケースを参照してください:

- Python版: `../python/testcases/`
- Verilog版: `../iverilog/testcases/`
