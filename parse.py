"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""

        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        while True:

            # Gets next symbol from definition file
            self.symbol = self.scanner.get_symbol()

            # At top level, symbol type can ONLY be HEADER
            if self.symbol.type == self.scanner.HEADER:

                # parse if HEADER is DEVICES, CONNECTIONS or MONITORS
                if self.symbol.id == self.scanner.DEVICES_ID or self.scanner.CONNECTIONS_ID \
                    or self.scanner.MONITORS_ID:

                    self.parse_section(self.symbol.id)
     
                # SYNTAX error - invalid HEADER name
                else:

                    pass

            # Or it's the end of the file
            elif self.symbol.type == self.scanner.EOF:

                # Handle not finding HEADER type errors here
                pass

        return True

    def parse_section(self, header_ID):

        # FIND symbol after HEADER that isn't a space
        self.symbol = self.scanner.get_symbol()
        while self.symbol is None:

            self.symbol = self.scanner.get_symbol()

        # Add error for invalid symbol after HEADER type
        if self.symbol != self.scanner.SECTION_START:

            pass

        if header_ID == self.scanner.DEVICES_ID:

            # parse for DEVICES
            self.parse_DEVICES_section()

        elif header_ID == self.scanner.CONNECTIONS_ID:

            # parse for CONNECTIONS
            self.parse_CONNECTIONS_section()

        elif header_ID == self.scanner.MONITORS_ID:

            # parse for MONITORS
            self.parse_MONITORS_section()

    def parse_DEVICES_section(self):
        pass

    def parse_CONNECTIONS_section(self):

        

        # FIND connection DEVICE 
        pass

    def parse_MONITORS_section(self):

        pass

    
