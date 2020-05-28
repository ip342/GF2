"""Test the parse module."""
import pytest

from names import Names
from scanner import Scanner
from network import Network
from devices import Devices
from parse import Parser
from monitors import Monitors
from errors import *


@pytest.fixture
def new_parser(path):
    """Return a new instance of the Parser class."""
    new_names = Names()
    new_scan = Scanner(path, new_names)
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    return Parser(new_names, new_devices, new_network, new_monitors, new_scan)


def test_find_header():
    """Checks for the appropriate HEADING sections in the definition file"""
    # Find headers DEVICES, CONNECTIONS and MONITORS
    parser = new_parser('test_files/test_HEADERS.txt')
    parser.parse_network()

    HEADERS_found = \
        parser.DEVICES_found and parser.CONNECTIONS_found and \
        parser.MONITORS_found

    assert HEADERS_found is True


@pytest.mark.parametrize("inputs, trial", [
    # SYN - "!"
    ("test_files/test_DEVICES_section_1.txt", 1),
    # SEM - defined device twice
    ("test_files/test_DEVICES_section_2.txt", 2),
    # SEM - invalid symbol (expected device)
    ("test_files/test_DEVICES_section_3.txt", 3),
    # SEM - no name or = after comma before ]
    ("test_files/test_DEVICES_section_4.txt", 4),
    # SEM - defined device twice for device after ,
    ("test_files/test_DEVICES_section_5.txt", 5),
    # SYN - no device set after equals
    ("test_files/test_DEVICES_section_6.txt", 6),
    # SYN - invalid device type
    ("test_files/test_DEVICES_section_7.txt", 7),
    # SYN - specifying DTYPE input
    ("test_files/test_DEVICES_section_8.txt", 8),
    # SEM - SWITCH only takes 0 or 1
    ("test_files/test_DEVICES_section_9.txt", 9),
    # SEM - gate more than 16 inputs
    ("test_files/test_DEVICES_section_10.txt", 10),
    # SYN - gate no inputs
    ("test_files/test_DEVICES_section_11.txt", 11),
    # SYN - no ending ;
    ("test_files/test_DEVICES_section_12.txt", 12),
    # SYN - no ending ; before ]
    ("test_files/test_DEVICES_section_13.txt", 13)
])
def test_DEVICES_errors(inputs, trial):
    """Tests for all the possible errors that can occur in DEVICES"""
    parser = new_parser(inputs)

    syntax = [1, 6, 7, 8, 11, 12, 13]
    semantic = [3, 4, 9, 10]

    # Requires 2 calls of parsing
    double_lined_checks = [2, 4]

    if trial in syntax:
        with pytest.raises(SyntaxError):
            parser.parse_DEVICES_section()

    elif trial in semantic:
        with pytest.raises(SemanticError):
            parser.parse_DEVICES_section()

    elif trial in double_lined_checks:
        parser.parse_DEVICES_section()
        with pytest.raises(SemanticError):
            parser.parse_DEVICES_section()


def test_DEVICES_section():
    """Test that the whole DEVICES parse_section runs"""
    parser = new_parser('test_files/test_DEVICES_section.txt')

    parser.parse_section('DEVICES')
    assert parser.scanner.error_count == 0


@pytest.mark.parametrize("inputs, trial", [
    # SEM - device doesn't exist
    ("test_files/test_CON_section_1.txt", 1),
    # SYN - no device name after word 'device'
    ("test_files/test_CON_section_2.txt", 2),
    # SYN - no { after device name
    ("test_files/test_CON_section_3.txt", 3),
    # SEM - not all inputs defined
    ("test_files/test_CON_section_4.txt", 4),
    # SYN - no ; to end connection line
    ("test_files/test_CON_section_5.txt", 5),
    # SEM - invalid port index
    ("test_files/test_CON_section_6.txt", 6),
    # SEM - port already connected
    ("test_files/test_CON_section_7.txt", 7),
    # SYN - invalid port name
    ("test_files/test_CON_section_8.txt", 8),
    # SYN - no . after device name
    ("test_files/test_CON_section_9.txt", 9),
    # SYN - con listed under wrong device
    ("test_files/test_CON_section_10.txt", 10),
    # SYN - no device after ->
    ("test_files/test_CON_section_11.txt", 11),
    # SYN - no -> between cons
    ("test_files/test_CON_section_12.txt", 12),
    # SYN - expected . after DTYPE
    ("test_files/test_CON_section_13.txt", 13),
    # SYN - invalid DTYPE output
    ("test_files/test_CON_section_14.txt", 14),
    # SYN - connection must start with dev name
    ("test_files/test_CON_section_15.txt", 15),
    # SYN - no } to end con subsection
    ("test_files/test_CON_section_16.txt", 16),
    # SEM - connection for device already assigned
    ("test_files/test_CON_section_17.txt", 17)
])
def test_CON_errors(inputs, trial):
    """Tests for all the possible errors that can occur in CONNECTIONS"""
    # Testing individual CON calls for errors
    parser = new_parser(inputs)

    syntax = [2, 3, 5, 8, 9, 10, 11, 12, 13, 14, 15]
    semantic = [1, 4, 6, 7]

    # Parse devices section first!
    parser.parse_section('DEVICES')

    if trial in syntax:
        with pytest.raises(SyntaxError):
            parser.parse_CONNECTIONS_section()

    elif trial in semantic:
        with pytest.raises(SemanticError):
            parser.parse_CONNECTIONS_section()

    elif trial == 16:
        with pytest.raises(SyntaxError):
            parser.parse_section('CONNECTIONS')

    elif trial == 17:
        with pytest.raises(SemanticError):
            parser.parse_section('CONNECTIONS')


def test_CON_section():
    """Test that the whole connections parse_section runs"""
    parser = new_parser('test_files/test_CON_section.txt')

    parser.parse_section('DEVICES')
    parser.parse_section('CONNECTIONS')
    assert parser.scanner.error_count == 0


@pytest.mark.parametrize("inputs, trial", [
    # SEM - device already set for monitoring
    ("test_files/test_MONITORS_section_1.txt", 1),
    # SEM - not a valid device
    ("test_files/test_MONITORS_section_2.txt", 2),
    # SYN - invalid DTYPE output
    ("test_files/test_MONITORS_section_3.txt", 3),
    # SYM - no . following DTYPE
    ("test_files/test_MONITORS_section_4.txt", 4),
    # SEM - invalid symbol
    ("test_files/test_MONITORS_section_5.txt", 5)
])
def test_MONITORS_errors(inputs, trial):
    """Tests for all the possible errors that can occur in MONITORS"""
    parser = new_parser(inputs)

    syntax = [3, 4]
    semantic = [1, 2, 5]

    # Parse devices section first!
    parser.parse_section('DEVICES')

    if trial in syntax:
        with pytest.raises(SyntaxError):
            parser.parse_section('MONITORS')

    elif trial in semantic:
        with pytest.raises(SemanticError):
            parser.parse_section('MONITORS')


def test_MONITORS_all():
    """Test that the 'all' keyword works in monitors'"""
    parser = new_parser('test_files/test_MONITORS_all.txt')

    parser.parse_network()
    assert len(parser.monitors.monitors_dictionary) == 6


def test_NETWORK():
    """Test that parse_network runs for a full definition file"""
    parser = new_parser('test_files/test_NETWORK.txt')

    parser.parse_network()
    assert parser.scanner.error_count == 0
