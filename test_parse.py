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


@pytest.mark.parametrize("definition_file, expected_output", [
    (""", True),
    ("", True),
    ("", True),
    ("", True)
])    