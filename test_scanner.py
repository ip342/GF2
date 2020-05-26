'''Test the scanner module'''

import pytest

from names import *
from scanner import *
from errors import *


@pytest.fixture
def test_names():
    """Return a new instance of the Names class."""
    names = Names()
    return names


@pytest.fixture
def test_symbol():
    """Return a new instance of the Symbol class."""
    symbol = Symbol()
    return symbol


@pytest.fixture
def test_scanner1():
    """Return a new instance of the Scanner class with test file 1 inputted."""
    test_file = 'test_scanner_text1.txt'
    names = Names()
    scan = Scanner(test_file, names)
    return scan


@pytest.fixture
def test_scanner2():
    """Return a new instance of the Scanner class with test file 2 inputted."""
    test_file = 'test_scanner_text2.txt'
    names = Names()
    scan = Scanner(test_file, names)
    return scan


@pytest.fixture
def test_scanner3():
    """Return a new instance of the Scanner class with test file 3 inputted."""
    test_file = 'test_scanner_text3.txt'
    names = Names()
    scan = Scanner(test_file, names)
    return scan


@pytest.fixture
def lines():
    """Test file 1 in list format."""
    return ['     d3 2342 inputs, ->', ' /l2534', ' 5..']


@pytest.fixture
def no_spaces():
    """Test file 1 formatted with no spaces."""
    return 'd32342inputs,->/l25345..'


def test_file_not_found(test_names):
    """Test that a file not found error works"""
    with pytest.raises(FileNotFoundError):
        Scanner("fakefile.txt", test_names)


def test_file_as_list(test_scanner1, test_names):
    """Test the file as list function works """
    test_scanner1.file_as_list == lines


def test_skip_spaces(test_scanner1, test_names, first_char="d"):
    """Test the self.skip_spaces() function of the scanner"""
    test_scanner1.skip_spaces()
    assert test_scanner1.current_character == first_char


def test_advance(test_scanner1, no_spaces):
    """Test the self.advance() function of the scanner"""
    i = 0
    for i in range(len(no_spaces)-1):
        current_char = no_spaces[i]
        test_scanner1.skip_spaces()
        assert test_scanner1.current_character == current_char
        test_scanner1.advance()
        i += 1


def test_get_name(test_scanner1, test_scanner2, test_names):
    """Test that the get_name function gives out the first name and next
    character"""
    test_scanner1.skip_spaces()
    name = test_scanner1.get_name()
    assert name[0] == "d3"
    assert name[1] == " "

    # move past square bracket and new line
    test_scanner2.get_symbol()
    test_scanner2.advance()
    name = test_scanner2.get_name()
    assert name[0] == "hello"
    assert name[1] == " "


def test_get_number(test_scanner1, test_names):
    """Test that the get_number function gives out a number and next
    character"""
    test_scanner1.skip_spaces()
    # move past name
    test_scanner1.get_symbol()
    test_scanner1.advance()
    number = test_scanner1.get_number()
    assert number[0] == "2342"
    assert number[1] == " "


def test_raise_comment_errors(test_scanner1, test_scanner2, test_names):
    """Test both comment errors"""
    # Only one '/' in single line comment
    with pytest.raises(CommentError):
        while test_scanner1.current_character != '':
            test_scanner1.get_symbol()
    # No '#' at end of multi line comment
    with pytest.raises(CommentError):
        while test_scanner2.current_character != '':
            test_scanner2.get_symbol()
        # get '\n' symbol
        test_scanner2.get_symbol()
        # get EOF to throw comment error
        test_scanner2.get_symbol()


def test_ignore_comment(test_scanner2, test_names):
    """Test that comment is ignored and next symbol recognised correctly"""
    next_symbol = test_scanner2.get_symbol()
    assert next_symbol.type == test_scanner2.CLOSE_SQUARE


def test_invalid_char_error(test_scanner3, test_names):
    """Test that arrow error is recognised"""
    with pytest.raises(SyntaxError):
        while test_scanner3.current_character != '':
            test_scanner3.get_symbol()


def test_line_and_char_count(test_scanner3, test_names):
    """Test that line and character counts are correct"""
    for i in range(9):
        test_scanner3.get_symbol()
    # actual line 8, counted as 7 for python indexing
    assert test_scanner3.current_line == 7
    # 7 characters plus '\n' character
    assert test_scanner3.current_character_number == 8
