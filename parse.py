"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from errors import SyntaxError, SemanticError


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

        self.DEVICES_found = False
        self.CONNECTIONS_found = False
        self.MONITORS_found = False

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

                    self.DEVICES_found = True
                    self.parse_section('DEVICES')

                elif self.symbol.id == self.scanner.CONNECTIONS_ID:

                    self.CONNECTIONS_found = True
                    self.parse_section('CONNECTIONS')

                elif self.symbol.id == self.scanner.MONITORS_ID:

                    self.MONITORS_found = True
                    self.parse_section('MONITORS')

            # Or it's the end of the file
            elif self.symbol.type == self.scanner.EOF:

                break

            # SYNTAX error - invalid HEADER name
            else:
                name = self.names.get_name_string(self.symbol.id)
                self.scanner.display_error(
                    SyntaxError, "%s is an invalid header" % name)

        return True

    def parse_section(self, header_ID):

        # FIND symbol after HEADER that isn't a space
        self.symbol = self.scanner.get_symbol()

        # Add error for symbol after HEADER that isn't OPEN_SQUARE
        if self.symbol.type != self.scanner.OPEN_SQUARE:

            self.scanner.display_error(
                SyntaxError, "Expecting opening square bracket after "
                             "section header")

        # Keeps parsing respective sections until doesn't return True (error)
        if header_ID == 'DEVICES':

            # parse for DEVICES
            while self.parse_DEVICES_section():
                pass

            print("\n END OF DEVICES \n")

        elif header_ID == 'CONNECTIONS':

            # parse for CONNECTIONS
            while self.parse_CONNECTIONS_section():
                pass

            print("\n END OF CONNECTIONS \n")

        elif header_ID == 'MONITORS':

            # parse for MONITORS
            while self.parse_MONITORS_section():
                pass

            print("\n END OF MONITORS \n")

    def parse_DEVICES_section(self):

        # Reading DEVICES section line by line..
        # First try to get a list of all devices on this line
        device_name_list = []

        # Distinguish between device_names and their type
        equals_encountered = False

        # Call to get list of all devices that occur before EQUALS
        while equals_encountered is False:
            self.symbol = self.scanner.get_symbol()
            
            if self.scanner is True:
                
                self.scanner.error = False
                return True
            
            # CHECK for NAME and append to device_name_list
            if self.symbol.type == self.scanner.NAME:

                device_name = self.scanner.names.get_name_string(
                    self.symbol.id)
                device_name_list.append(device_name)

            # Continue through COMMA
            elif self.symbol.type == self.scanner.COMMA:

                continue

            elif self.symbol.type == self.scanner.CLOSE_SQUARE:

                return False

            elif self.symbol.type == self.scanner.EOF:

                return False

            # Trigger to exit loop and look for device type
            elif self.symbol.type == self.scanner.EQUALS:

                equals_encountered = True

            else:

                # Some error message about invalid symbols
                self.scanner.display_error(
                    SemanticError, "Invalid symbol - "
                    "expecting a device or list of devices.")
                return True

        self.symbol = self.scanner.get_symbol()

        device_id_list = self.devices.names.lookup(device_name_list)

        if type(device_id_list) == int:
            device_id_list = [device_id_list]

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
                    self.devices.add_output(device_id, None)

            elif self.symbol.id == self.devices.CLOCK:

                # Make it 1 for now
                self.devices.make_clock(device_id, 1)

            elif self.symbol.id == self.devices.SWITCH:

                # Same as above, set switch off for now
                self.devices.make_switch(device_id, 0)

            else:

                # Error for invalid device
                invalid_device = self.scanner.names.get_name_string(
                    self.symbol.id)
                self.scanner.display_error(
                    SyntaxError, "%s is an "
                    "invalid device type." % invalid_device)
                return True

        # Device parameter..
        devices_no_parameter = [self.devices.D_TYPE, self.devices.XOR]
        if self.symbol.id not in devices_no_parameter:
            self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.NUMBER:

            n = int(self.symbol.id)

            for device_id in device_id_list:

                if self.devices.get_device(device_id).device_kind \
                        == self.devices.D_TYPE:

                    self.scanner.display_error(
                        SemanticError, "Cannot specify inputs for DTYPE.")
                    return True

                elif self.devices.get_device(device_id).device_kind \
                        == self.devices.SWITCH:

                    if n == 0:

                        continue

                    elif n == 1:

                        self.devices.set_switch(device_id, 1)

                    else:

                        self.scanner.display_error(
                            SemanticError, "Switch can only take state 0 or 1")
                        return True

                elif self.devices.get_device(device_id).device_kind \
                        == self.devices.XOR:

                    self.scanner.display_error(
                        SemanticError, "Cannot specify inputs for XOR")
                    return True

                elif self.devices.get_device(device_id).device_kind \
                        == self.devices.CLOCK:

                    # Set clock cycle..
                    clock_device = self.devices.get_device(device_id)
                    clock_device.clock_half_period = n

                elif self.devices.get_device(device_id) is None:

                    self.scanner.display_error(
                        SemanticError, "Device doesn't exist.")
                    return True

                else:

                    # Gates can only have 1-16 inputs
                    if n > 16:

                        self.scanner.display_error(
                            SemanticError, "Device can only have 1-16 inputs.")
                        return True

                    # Add all the inputs to the device..
                    else:

                        for input_num in range(1, n + 1):
                            input_id = self.devices.names.lookup(
                                ["I"+str(input_num)])

                            self.devices.add_input(device_id, input_id)
                            self.devices.add_output(device_id, None)

        self.symbol = self.scanner.get_symbol()

        return True

    def parse_CONNECTIONS_section(self):

        # CHECK for word device
        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.CLOSE_SQUARE:
            
            if self.network.check_network():
                print('Network Connected')

            return False

        if self.symbol.type == self.scanner.EOF:

            return False

        elif self.symbol.id != self.scanner.DEVICE:  # Revist this
            self.scanner.display_error(
                SyntaxError, "List of connections must start "
                             "with the word 'device'.")
            return True

        # CHECK for device name
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.NAME:
            self.con_device = self.devices.get_device(self.symbol.id)
            if self.con_device is None:
                con_device_name = self.names.get_name_string(self.symbol.id)
                self.scanner.display_error(
                    SemanticError, "Device '{}' does not exist."
                                   .format(con_device_name))
                return True
        else:
            self.scanner.display_error(
                SyntaxError, "Expected a device name after the word 'device'.")
            return True

        # CHECK for opening curly bracket
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.OPEN_CURLY:
            self.scanner.display_error(
                SyntaxError, "Expected '{' after device name.")
            return True

        # PARSE each line encompassed by curly brackets
        while self.parse_Connections_lines():
            pass

        return True

    def parse_MONITORS_section(self):

        # GET next symbol (after OPEN_SQUARE)
        self.symbol = self.scanner.get_symbol()

        # CHECK for NAME
        if self.symbol.type == self.scanner.NAME:

            # CHECK for ID error, if none, proceed to fetch device object
            if self.symbol.id is None:

                name = self.scanner.names.get_name_string(self.symbol.id)
                self.scanner.display_error(
                    SemanticError, "%s is not a valid device." % name)
                return True

            device = self.devices.get_device(self.symbol.id)

            # CHECK for device - get_device returns None for invalid device_id
            if device is None:

                name = self.scanner.names.get_name_string(self.symbol.id)
                self.scanner.display_error(
                    SemanticError, "%s is not a valid device." % name)
                return True

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

                        self.scanner.display_error(
                            SemanticError, "DTYPE can only use .Q or .QBAR")

                # Error for DTYPE not being followed by DOT
                else:

                    self.scanner.display_error(
                        SemanticError, "DTYPE must be followed by .")

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

        elif self.symbol.type == self.scanner.EOF:

            return False

        # Error for unexpected symbol
        else:

            self.scanner.display_error(
                SemanticError, "Invalid symbol")

        return True

    def parse_Connections_lines(self):

        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.CLOSE_CURLY:
            return False

        # CHECK for start connection
        elif self.symbol.type != self.scanner.NAME:
            self.scanner.display_error(
                SyntaxError, "Connection must start with a device name.")
            return True
        start_con = self.devices.get_device(self.symbol.id)
        if start_con is None:
            print(self.symbol.id)
            start_con_name = self.names.get_name_string(self.symbol.id)
            self.scanner.display_error(
                SemanticError, "Device '{}' does not exist."
                               .format(start_con_name))
            return True
        elif start_con.device_kind == self.devices.D_TYPE:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.type != self.scanner.DOT:
                self.scanner.display_error(
                    SyntaxError, "Expected '.' after DTYPE name.")
                return True
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id not in self.devices.dtype_output_ids:
                self.scanner.display_error(
                    SyntaxError, "Invalid DTYPE output name")
                return True
            start_con_port_id = self.symbol.id
        else:
            start_con_port_id = None

        # CHECK for arrow
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.ARROW:
            self.scanner.display_error(
                SyntaxError, "Expected '->' inbetween "
                             "start and end connections.")
            return True

        # CHECK for end connection
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.NAME:
            self.scanner.display_error(
                SyntaxError, "A device name must follow "
                             "the connection arrow.")
            return True
        end_con = self.devices.get_device(self.symbol.id)
        end_con_name = self.names.get_name_string(self.symbol.id)
        if end_con is None:
            self.scanner.display_error(
                SemanticError, "Device '{}' does not exist."
                               .format(end_con_name))
            return True
        if end_con != self.con_device:
            self.scanner.display_error(
                SyntaxError, "This connection has been listsed under the "
                             "incorrect device subsection.")
            return True
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.DOT:
            self.scanner.display_error(
                SyntaxError, "Expected '.' after device name")
            return True
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type != self.scanner.NAME:
            self.scanner.display_error(
                SyntaxError, "Invalid port name.")
            return True
        end_con_port_id = self.symbol.id
        con_status = self.network.make_connection(
                     start_con.device_id, start_con_port_id,
                     end_con.device_id, end_con_port_id)
        if con_status == self.network.INPUT_CONNECTED:
            self.scanner.display_error(
                SemanticError, "{}.{} is already connected.".format(
                               end_con_name,
                               self.devices.names.get_name_string
                               (end_con_port_id)))
            return True
        elif con_status == self.network.PORT_ABSENT:
            self.scanner.display_error(
                SemanticError, "Invalid port index.")
            return True
        elif con_status == self.network.NO_ERROR:
            pass

        # CHECK for semicolon
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self.scanner.display_error(
                SyntaxError, "Expected ';' to end connection line.")
            return True

        return True
