"""
Matrix operations test - Heavy computation
Tests matrix multiplication and numerical operations
"""

def matrix_multiply(a, b):
    """行列の積を計算"""
    rows_a = len(a)
    cols_a = len(a[0])
    rows_b = len(b)
    cols_b = len(b[0])
    
    if cols_a != rows_b:
        raise ValueError("Matrix dimensions don't match")
    
    result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]
    
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    
    return result


def matrix_power(matrix, n):
    """行列のn乗を計算"""
    size = len(matrix)
    result = [[1 if i == j else 0 for j in range(size)] for i in range(size)]
    
    for _ in range(n):
        result = matrix_multiply(result, matrix)
    
    return result


def fibonacci_matrix(n):
    """行列累乗を使ったフィボナッチ数列計算"""
    if n <= 1:
        return n
    
    # フィボナッチ行列
    fib_matrix = [[1, 1], [1, 0]]
    
    # n-1乗を計算
    result = matrix_power(fib_matrix, n - 1)
    
    return result[0][0]


def compute_primes(limit):
    """エラトステネスの篩で素数を計算"""
    sieve = [True] * limit
    sieve[0] = sieve[1] = False
    
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit, i):
                sieve[j] = False
    
    return [i for i in range(limit) if sieve[i]]


def test_matrix_operations():
    """重い行列演算と計算のテスト（約10秒）"""
    # 大きな素数計算（重い処理）
    primes = compute_primes(1000000)
    assert len(primes) > 70000  # 100万以下の素数は約78,000個
    
    # 300x300行列の生成と計算（非常に重い）
    size = 300
    matrix_a = [[i + j for j in range(size)] for i in range(size)]
    matrix_b = [[i - j for j in range(size)] for i in range(size)]
    
    # 行列積の計算（O(n^3)の計算量）
    result = matrix_multiply(matrix_a, matrix_b)
    
    # 検証
    assert len(result) == size
    assert len(result[0]) == size
    
    # フィボナッチ数列の複数回計算
    fib_values = []
    for n in range(20, 35):
        fib_n = fibonacci_matrix(n)
        fib_values.append(fib_n)
    
    assert fib_values[-1] > 5000000  # F(34) = 5,702,887
    
    # 複数の中規模行列演算
    for _ in range(5):
        small_matrix = [[2, 1], [1, 2]]
        power_result = matrix_power(small_matrix, 20)
        assert power_result[0][0] > 0
    
    print("All heavy matrix operation tests passed!")


if __name__ == "__main__":
    test_matrix_operations()
