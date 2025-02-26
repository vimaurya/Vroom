import pytest
import source.funcs as funcs

def test_add():
    result = funcs.add(1, 3)
    assert result == 4
    
def test_add_strings():
    result = funcs.add("Something ", "silly")
    assert result == "Something silly"
    
def test_divide():
    result = funcs.divide(3,3)
    assert result == 1
    
def test_divide_by_zero():
    with pytest.raises(ValueError):
        funcs.divide(3,0)
    