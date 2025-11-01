#!/usr/bin/env python3
"""
Simple calculator test
Tests basic arithmetic operations
"""

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

if __name__ == "__main__":
    # Test cases
    assert add(2, 3) == 5
    assert subtract(5, 3) == 2
    assert multiply(4, 5) == 20
    assert divide(10, 2) == 5
    
    print("All tests passed!")
