import pytest
from ..source import shapes
import math


class TestCircle:
    
    def setup_method(self, method):
        print(f"Setting up {method}")
        self.circle = shapes.Circle(10)
        
        
    def teardown_method(self, method):
        del self.circle
    
    def test_area(self):
        assert self.circle.area() == math.pi * self.circle.radius ** 2
        
        
    def test_perimeter(self):
        result = self.circle.perimeter()
        assert result == math.pi * self.circle.radius * 2
        
         