'''Test the scanner module'''

import pytest

from names import *
from scanner import *
from errors import *

@pytest.fixture
def test_names():
    names = Names()
    return names

@pytest.fixture
def test_symbol():
    symbol = Symbol()
    return symbol

@pytest.fixture
def test_scanner():
    test_file = 'test_scanner_text.txt'
    names = Names()
    scan = Scanner(test_file, names)
    return scan

@pytest.fixture
def no_spaces():
    return 'd32342inputs,->l2534..'


def file_not_found(test_names):
    """Test that a file not found error works"""
    with pytest.raises(FileNotFoundError):
        Scanner("fakefile.txt", test_names)


def file_as_list(test_scanner, test_names, second_line=' l2534', third_line=' 5..')
    """Test that the file as list function works """
    test_scanner.file_as_list[1] == second_line
    test_scanner.file_as_list[2] == third_line

def test_skip_spaces(test_scanner, test_names, first_char="d"):
    """Test the self.skip_spaces() function of the scanner"""
    test_scanner.skip_spaces()
    assert test_scanner.current_character == first_char


def test_advance(test_scanner, no_spaces):
    """Test the self.advance() functionality of the scanner class"""
    i = 0
    while i <= len(no_spaces)-1:
        expected = no_spaces[i]
        test_scanner.skip_spaces()
        assert test_scanner.current_character == expected
        test_scanner.advance()
        i += 1

def test_get_name_and_number(test_scanner, test_names):
    """check that the get_name function gives out a valid name and the next character,
    check that the name is an alphanumerical string"""
    test_scanner.skip_spaces()
    name = test_scanner.get_name()
    assert name[0] == "d3"
    assert name[1] == " "
    assert name[0].isalnum()
    test_scanner.advance()
    number = test_scanner.get_number()
    assert number[0] == "2342"
    assert number[1] == " "