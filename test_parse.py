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

    # Find headers DEVICES, CONNECTIONS and MONITORS
    parser = new_parser('parser_test_files/test_HEADERS.txt')
    parser.parse_network()

    HEADERS_found = \
        parser.DEVICES_found and parser.CONNECTIONS_found and \
        parser.MONITORS_found

    assert HEADERS_found is True


@pytest.mark.parametrize("inputs, trial", [("parser_test_files/test_DEVICES_section_1.txt", 1),    # SYN - "!"
                                           ("parser_test_files/test_DEVICES_section_2.txt", 2),    # SEM - defined device twice
                                           ("parser_test_files/test_DEVICES_section_3.txt", 3),    # SEM - invalid symbol (expected device)
                                           ("parser_test_files/test_DEVICES_section_4.txt", 4),    # SEM - no name or = after comma before ]
                                           ("parser_test_files/test_DEVICES_section_5.txt", 5),    # SEM - defined device twice for device after ,
                                           ("parser_test_files/test_DEVICES_section_6.txt", 6),    # SYN - no device set after equals
                                           ("parser_test_files/test_DEVICES_section_7.txt", 7),    # SYN - invalid device type
                                           ("parser_test_files/test_DEVICES_section_8.txt", 8),    # SYN - specifying DTYPE input
                                           ("parser_test_files/test_DEVICES_section_9.txt", 9),    # SEM - SWITCH only takes 0 or 1
                                           ("parser_test_files/test_DEVICES_section_10.txt", 10),  # SEM - gate more than 16 inputs
                                           ("parser_test_files/test_DEVICES_section_11.txt", 11),  # SYN - gate no inputs
                                           ("parser_test_files/test_DEVICES_section_12.txt", 12),  # SYN - no ending ;
                                           ("parser_test_files/test_DEVICES_section_13.txt", 13)   # SYN - no ending ; before ]
                                           ])
def test_DEVICES_errors(inputs, trial):

    # Testing individual DEVICE calls for errors
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

    # Whole section should pass
    parser = new_parser('parser_test_files/test_DEVICES_section.txt')

    parser.parse_section('DEVICES')
    assert parser.scanner.error_count == 0


@pytest.mark.parametrize("inputs, trial", [("parser_test_files/test_CON_section_1.txt", 1),    # SEM - device doesn't exist
                                           ("parser_test_files/test_CON_section_2.txt", 2),    # SYN - no device name after word 'device'
                                           ("parser_test_files/test_CON_section_3.txt", 3),    # SYN - no { after device name
                                           ("parser_test_files/test_CON_section_4.txt", 4),    # SEM - not all inputs defined
                                           ("parser_test_files/test_CON_section_5.txt", 5),    # SYN - no ; to end connection line
                                           ("parser_test_files/test_CON_section_6.txt", 6),    # SEM - invalid port index
                                           ("parser_test_files/test_CON_section_7.txt", 7),    # SEM - port already connected
                                           ("parser_test_files/test_CON_section_8.txt", 8),    # SYN - invalid port name
                                           ("parser_test_files/test_CON_section_9.txt", 9),    # SYN - no . after device name
                                           ("parser_test_files/test_CON_section_10.txt", 10),  # SYN - con listed under wrong device
                                           ("parser_test_files/test_CON_section_11.txt", 11),  # SYN - no device after ->
                                           ("parser_test_files/test_CON_section_12.txt", 12),  # SYN - no -> between cons
                                           ("parser_test_files/test_CON_section_13.txt", 13),  # SYN - expected . after DTYPE
                                           ("parser_test_files/test_CON_section_14.txt", 14),  # SYN - invalid DTYPE output
                                           ("parser_test_files/test_CON_section_15.txt", 15),  # SYN - connection must start with dev name
                                        #    ("parser_test_files/test_CON_section_16.txt", 16),  #
                                        #    ("parser_test_files/test_CON_section_17.txt", 17)   #
                                           ])
def test_CON_errors(inputs, trial):

    # Testing individual CON calls for errors
    parser = new_parser(inputs)

    syntax = [2, 3, 5, 8, 9, 10, 11, 12, 13, 14, 15]
    semantic = [1, 4, 6, 7]

    if trial in syntax:
        # Parse devices section first!
        parser.parse_section('DEVICES')
        with pytest.raises(SyntaxError):
            parser.parse_CONNECTIONS_section()

    elif trial in semantic:
        parser.parse_section('DEVICES')
        with pytest.raises(SemanticError):
            parser.parse_CONNECTIONS_section()
