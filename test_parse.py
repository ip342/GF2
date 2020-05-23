"""Test the parse module."""
import pytest

from names import Names
from scanner import Scanner
from network import Network
from devices import Devices
from parse import Parser
from monitors import Monitors


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
    parser = new_parser('parser_test_files/test_def_file.txt')
    parser.parse_network()

    HEADERS_found = \
        parser.DEVICES_found and parser.CONNECTIONS_found and \
        parser.MONITORS_found

    assert HEADERS_found is True


# Doesn't work, not sure why?
def test_DEVICES_section():

    # Should pass
    parser = new_parser('parser_test_files/test_DEVICES_section_1.txt')
    parser.parse_DEVICES_section()
    parser.parse_DEVICES_section()
    parser.parse_DEVICES_section()
    parser.parse_DEVICES_section()
    parser.parse_DEVICES_section()
    
    assert parser.scanner.error_count == 0

    parser.parse_DEVICES_section()
    
    assert parser.scanner.error_count == 0

    parser.parse_DEVICES_section()
    
    assert parser.scanner.error_count == 0

    # Missing [] brackets - throws SyntaxError
    # parser = new_parser('parser_test_files/test_DEVICES_section_2.txt')
    # with pytest.raises(SyntaxError):
    #     parser.parse_section('DEVICES')
