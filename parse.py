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
                if self.symbol.id == self.scanner.DEVICES_ID:

                    self.parse_section('DEVICES')

                elif self.symbol.id == self.scanner.CONNECTIONS_ID:

                    self.parse_section('CONNECTIONS')

                elif self.symbol.id == self.scanner.MONITORS_ID:

                    self.parse_section('MONITORS')

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

        # Add error for symbol after HEADER that isn't OPEN_SQUARE
        if self.symbol != self.scanner.OPEN_SQUARE:

            pass

        # Keeps parsing respective sections until doesn't return True (error)
        if header_ID == 'DEVICES':

            # parse for DEVICES
            while self.parse_DEVICES_section():
                pass

        elif header_ID == 'CONNECTIONS':

            # parse for CONNECTIONS
            while self.parse_CONNECTIONS_section():
                pass

        elif header_ID == 'MONITORS':

            # parse for MONITORS
            while self.parse_MONITORS_section():
                pass

    def parse_DEVICES_section(self):

        # Reading DEVICES section line by line..

        # First try to get a list of all devices on this line
        device_name_list = []

        # Distinguish between device_names and their type
        equals_encountered = False

        # Call to get list of all devices that occur before EQUALS
        while equals_encountered is False:
            self.symbol = self.scanner.get_symbol()

            # Skip spaces
            if self.symbol is None:

                continue

            # CHECK for NAME and append to device_name_list
            elif self.symbol.type == self.scanner.NAME:

                device_name = self.scanner.names.get_name_string(
                    self.symbol.id)
                device_name_list.append(device_name)

            # Continue through COMMA
            elif self.symbol.type == self.scanner.COMMA:

                continue

            # Trigger to exit loop and look for device type
            elif self.symbol.type == self.scanner.EQUALS:

                equals_encountered = True

            else:

                # Some error message about invalid symbols
                self.scanner.display_error(SemanticError, "Invalid symbol \
                    expecting a device or list of devices.")

        self.symbol = self.scanner.get_symbol()
        device_id_list = self.devices.names.lookup(device_name_list)

        # Make devices
        for device_id in device_id_list:

            if self.symbol.id == self.devices.D_TYPE:

                self.devices.make_d_type(device_id)

            elif self.symbol.id in self.devices.gate_types:
                self.devices.add_device(device_id, self.symbol.id)

                # Special case for XOR gate
                if self.symbol.id == self.devices.XOR:

                    # Adding the 2 inputs to names list and getting IDs
                    I1, I2 = self.devices.names.lookup(["I1", "I2"])
                    self.devices.add_input(device_id, I1)
                    self.devices.add_input(device_id, I2)

            elif self.symbol.id == self.devices.CLOCK:

                # Need to figure out how to do this..
                # Grab clock period then..? half_period?

                # Make it 1 for now
                self.devices.make_clock(device_id, 1)

            elif self.symbol.id == self.devices.SWITCH:

                # Same as above, set switch off for now
                self.devices.make_switch(device_id, 0)

            else:

                # Error for invalid device
                invalid_device = self.scanner.names.get_name_string(
                    self.symbol.id)
                self.scanner.display_error(SyntaxError, "%s is an \
                    invalid device type." % invalid_device)

        # Device parameter..
        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.NUMBER:

            n = int(self.scanner.get_number())

            for device_id in device_id_list:

                if self.devices.get_device(device_id).device_kind == self.devices.D_TYPE:

                    self.scanner.display_error(
                        SemanticError, "Cannot specify inputs for DTYPE.")

                elif self.devices.get_device(device_id).device_kind == self.devices.SWITCH:

                    if n == 0:

                        continue

                    elif n == 1:

                        self.devices.set_switch(device_id, 1)

                    else:

                        self.scanner.display_error(
                            SemanticError, "Switch can only take state 0 or 1")

                elif self.devices.get_device(device_id).device_kind == self.devices.XOR:

                    self.scanner.display_error(
                        SemanticError, "Cannot specify inputs for XOR")

                elif self.devices.get_device(device_id).device_kind == self.devices.CLOCK:

                    # Set clock cycle..
                    clock_device = self.devices.get_device(device_id)
                    clock_device.clock_half_period = n

                elif self.devices.get_device(device_id) is None:

                    self.scanner.display_error(
                        SemanticError, "Device doesn't exist.")

                else:

                    # Gates can only have 1-16 inputs
                    if n > 16:

                        self.scanner.display_error(
                            SemanticError, "Device can only have 1-16 inputs.")

                    # Add all the inputs to the device..
                    else:

                        for input_num in range(1, n + 1):
                            [input_id] = self.devices.names.lookup(
                                ["I"+str(input_num)])

                            self.devices.add_input(device_id, input_id)

    def parse_CONNECTIONS_section(self):

        # FIND connection DEVICE
        pass

    def parse_MONITORS_section(self):

        # GET next symbol (after OPEN_SQUARE)
        self.symbol = self.scanner.get_symbol()

        # CHECK for NAME
        if self.symbol.type == self.scanner.NAME:

            # CHECK for ID error, if none, proceed to fetch device object
            if self.symbol.id is None:

                pass

            device = self.devices.get_device(self.symbol.id)

            # CHECK for device - get_device returns None for invalid device_id
            if device is None:

                pass

            # Special case if NAME is DTYPE as can have .Q or .QBAR appended
            if device.device_kind == self.devices.D_TYPE:

                # Track device_id here to create monitor later
                device_id = self.symbol.id

                # GET next symbol and CHECK it's DOT
                self.symbol = self.scanner.get_symbol()
                if self.symbol.type == self.scanner.DOT:

                    # Symbol following DTYPE and DOT must be Q or QBAR
                    self.symbol = self.scanner.get_symbol()
                    if self.symbol.id in self.devices.dtype_output_ids:

                        # Make monitor for device with output..
                        self.monitors.make_monitor(device_id, self.symbol.id)

                    # Error if symbol after DOT is not Q or QBAR
                    else:

                        pass

                # Error for DTYPE not being followed by DOT
                else:

                    pass

            # For devices that are not DTYPE, make monitor with output_id None
            else:

                self.monitors.make_monitor(self.symbol.id, None)

                # NEED TO ADD ERRORS SOMEWHERE HERE..

        # CHECK for COMMA
        elif self.symbol.type == self.scanner.COMMA:

            # Return True here to continue to next symbol
            return True

        # CHECK for SEMICOLON
        elif self.symbol.type == self.scanner.SEMICOLON:

            return True

        # Checks for CLOSE_SQUARE for end of section
        elif self.symbol.type == self.scanner.CLOSE_SQUARE:

            # Exits parse_section while loop
            return False

        # Error for unexpected symbol
        else:

            pass

        return True
