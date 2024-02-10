# test_math_operations.py
import pytest
from operation import add_numbers

def test_add_numbers():
    result = add_numbers(2,  3)
    assert result ==  5
