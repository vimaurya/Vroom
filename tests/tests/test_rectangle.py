import pytest
from ..source import shapes

def test_area():
    length = 5
    width = 4
    res = shapes.Rectangle(length, width)
    
    assert res.area() == length * width