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
def lines():
    return ['     d3 2342 inputs, ->', ' /l2534', ' 5..']

@pytest.fixture
def no_spaces():
    return 'd32342inputs,->/l25345..'


def test_file_not_found(test_names):
    """Test that a file not found error works"""
    with pytest.raises(FileNotFoundError):
        Scanner("fakefile.txt", test_names)


def test_file_as_list(test_scanner, test_names):
    """Test the file as list function works """
    test_scanner.file_as_list == lines


def test_skip_spaces(test_scanner, test_names, first_char="d"):
    """Test the self.skip_spaces() function of the scanner"""
    test_scanner.skip_spaces()
    assert test_scanner.current_character == first_char


def test_advance(test_scanner, no_spaces):
    """Test the self.advance() function of the scanner"""
    i = 0
    for i in range(len(no_spaces)-1):
        current_char = no_spaces[i]
        test_scanner.skip_spaces()
        assert test_scanner.current_character == current_char
        test_scanner.advance()
        i += 1


def test_get_name_and_number(test_scanner, test_names):
    """check that the get_name function gives out a valid name and the next character,
    check that the name is an alphanumerical string"""
    test_scanner.skip_spaces()
    name = test_scanner.get_name()
    assert name[0] == "d3"
    assert name[1] == " "
    test_scanner.advance()
    number = test_scanner.get_number()
    assert number[0] == "2342"
    assert number[1] == " "

def test_raise_comment_error(test_scanner, test_names):
    
    with pytest.raises(CommentError):
        while test_scanner.current_character != '':
            test_scanner.get_symbol()