#!/usr/bin/env python3
"""
String manipulation test
Tests basic string operations
"""

def reverse_string(s):
    return s[::-1]

def count_vowels(s):
    vowels = 'aeiouAEIOU'
    return sum(1 for c in s if c in vowels)

def is_palindrome(s):
    s = s.lower().replace(' ', '')
    return s == s[::-1]

if __name__ == "__main__":
    # Test cases
    assert reverse_string("hello") == "olleh"
    assert count_vowels("hello world") == 3
    assert is_palindrome("racecar") == True
    assert is_palindrome("hello") == False
    
    print("All tests passed!")
