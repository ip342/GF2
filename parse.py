"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from errors import *


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

        self.all_devices_list = []
        self.all_cons_list = []
        self.all_monitors_list = []
        self.does_not_exist_list = []

    def parse_network(self):
        """Parse the circuit definition file.

        Calls sections DEVICES, CONNECTIONS and MONITORS
        individually. Returns True if definition file parses successfully
        without errors, and False otherwise.
        """
        sections = ['DEVICES', 'CONNECTIONS', 'MONITORS']
        sections_found = []

        while True:
            # Gets next symbol from definition file
            self.symbol = self.scanner.get_symbol(["]", ""])

            while self.scanner.error is True:
                self.scanner.error = False
                self.symbol = self.scanner.get_symbol(["]", ""])

            # At top level, symbol type can ONLY be HEADER
            if self.symbol.type == self.scanner.HEADER:
                # parse if HEADER is DEVICES, CONNECTIONS or MONITORS
                if self.symbol.id == self.scanner.DEVICES_ID:
                    if self.DEVICES_found:
                        self.scanner.display_error(
                            NetworkError, "DEVICES already defined.")

                    else:
                        self.DEVICES_found = True
                        self.parse_section('DEVICES')
                    sections_found.append('DEVICES')

                elif self.symbol.id == self.scanner.CONNECTIONS_ID:
                    if self.CONNECTIONS_found:
                        self.scanner.display_error(
                            NetworkError, "CONNECTIONS already defined.")

                    if self.DEVICES_found:
                        self.CONNECTIONS_found = True
                        self.parse_section('CONNECTIONS')

                    else:
                        self.scanner.display_error(
                            NetworkError, "Cannot define CONNECTIONS "
                            "before DEVICES.")
                    sections_found.append('CONNECTIONS')

                elif self.symbol.id == self.scanner.MONITORS_ID:
                    if self.MONITORS_found:
                        self.scanner.display_error(
                            NetworkError, "MONITORS already defined.")

                    if self.CONNECTIONS_found:
                        self.MONITORS_found = True
                        self.parse_section('MONITORS')

                    else:
                        self.scanner.display_error(
                            NetworkError, "Cannot define MONITORS "
                            "before CONNECTIONS.")
                    sections_found.append('MONITORS')

            # Or it's the end of the file
            elif self.symbol.type == self.scanner.EOF:
                # Check all sections have been found
                for section in sections:
                    if section not in sections_found:

                        self.scanner.display_error(
                            NetworkError, '%s section missing' % section)

                break

            elif self.symbol.type == self.scanner.NAME:
                name = self.names.get_name_string(self.symbol.id)
                self.scanner.display_error(
                    SyntaxError, "%s is an invalid header" % name, ["]", ""])

            # SYNTAX error - invalid HEADER name
            else:
                self.scanner.display_error(
                    SyntaxError, "Expected a header", ["]", ""])

        return True

    def parse_section(self, header_ID):
        """Parse a section.

        Parse a section of the circuit definition file enclosed by
        square brackets, and build corresponding part of the
        circuit.
        """
        # FIND symbol after HEADER that isn't a space
        self.symbol = self.scanner.get_symbol(["]", ""])

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        # Add error for symbol after HEADER that isn't OPEN_SQUARE
        if self.symbol.type != self.scanner.OPEN_SQUARE:
            self.scanner.display_error(
                SyntaxError, "Expecting opening square bracket after "
                             "section header")
            return

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
        """Parse and build the DEVICES section line by line."""
        # First try to get a list of all devices on this line
        device_name_list = []

        # Distinguish between device_names and their type
        equals_encountered = False

        self.symbol = self.scanner.get_symbol()

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        # CHECK for NAME and append to device_name_list
        if self.symbol.type == self.scanner.NAME:
            device_name = self.scanner.names.get_name_string(
                self.symbol.id)
            if device_name in self.all_devices_list:
                self.scanner.display_error(
                    SemanticError, "Device name '{}' has already "
                                   "been assigned.".format(device_name))
                return True

            device_name_list.append(device_name)
            self.all_devices_list.append(device_name)

        elif self.symbol.type == self.scanner.CLOSE_SQUARE:
            return False

        elif self.symbol.type == self.scanner.EOF:
            return False

        else:
            # Some error message about invalid symbols
            self.scanner.display_error(
                SemanticError, "Expecting a device name.")
            return True

        # Call to get list of all devices that occur before EQUALS
        while equals_encountered is False:
            self.symbol = self.scanner.get_symbol()
            if self.scanner.error is True:
                self.scanner.error = False
                return True

            # Continue through COMMA
            if self.symbol.type == self.scanner.COMMA:
                pass

            elif self.symbol.type == self.scanner.CLOSE_SQUARE:
                self.scanner.display_error(
                    SemanticError, "Expecting comma or equals.")
                return False

            elif self.symbol.type == self.scanner.EOF:
                self.scanner.display_error(
                    SemanticError, "Expecting comma or equals.")
                return False

            # Trigger to exit loop and look for device type
            elif self.symbol.type == self.scanner.EQUALS:
                equals_encountered = True

            else:
                # Some error message about invalid symbols
                self.scanner.display_error(
                    SemanticError, "Expecting comma or equals.")
                return True

            if equals_encountered is False:
                self.symbol = self.scanner.get_symbol()
                if self.scanner.error is True:
                    self.scanner.error = False
                    return True

                # CHECK for NAME and append to device_name_list
                if self.symbol.type == self.scanner.NAME:
                    device_name = self.scanner.names.get_name_string(
                        self.symbol.id)
                    if device_name in self.all_devices_list:
                        self.scanner.display_error(
                            SemanticError, "Device name '{}' has already been "
                                           "assigned.".format(device_name))
                        return True

                    device_name_list.append(device_name)
                    self.all_devices_list.append(device_name)

                else:
                    # Some error message about invalid symbols
                    self.scanner.display_error(
                        SemanticError, "Expecting a device name.")
                    return True

        self.symbol = self.scanner.get_symbol()

        if self.scanner.error is True:
            self.scanner.error = False
            return True

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
                    self.devices.add_output(device_id, None)

            elif self.symbol.id == self.devices.CLOCK:
                # Make it 1 for now
                self.devices.make_clock(device_id, 1)

            elif self.symbol.id == self.devices.SIGGEN:
                # Make it 1 for now
                self.devices.make_siggen(device_id, "1")

            elif self.symbol.id == self.devices.SWITCH:
                # Same as above, set switch off for now
                self.devices.make_switch(device_id, 0)

            elif self.symbol.type == self.scanner.SEMICOLON:
                self.scanner.display_error(
                    SyntaxError, "Expected a device type")
                return True

            elif self.symbol.type == self.scanner.NAME:
                # Error for invalid device
                invalid_device = self.scanner.names.get_name_string(
                    self.symbol.id)
                self.scanner.display_error(
                    SyntaxError, "%s is an "
                    "invalid device type." % invalid_device)
                return True

            else:
                self.scanner.display_error(
                    SyntaxError, "Expected a device type")
                return True

        # Device parameter..
        devices_no_parameter = [self.devices.D_TYPE, self.devices.XOR]
        if self.symbol.id not in devices_no_parameter:
            self.symbol = self.scanner.get_symbol()

            if self.scanner.error is True:
                self.scanner.error = False
                return True

            if self.symbol.type == self.scanner.NUMBER:
                n = int(self.symbol.id)

                for device_id in device_id_list:
                    if self.devices.get_device(device_id).device_kind \
                            == self.devices.SWITCH:
                        if n == 0:
                            continue

                        elif n == 1:
                            self.devices.set_switch(device_id, 1)

                        else:
                            self.scanner.display_error(
                                SemanticError, "Switch can only take "
                                               "state 0 or 1")
                            return True

                    elif self.devices.get_device(device_id).device_kind \
                            == self.devices.CLOCK:
                        # Set clock cycle..
                        clock_device = self.devices.get_device(device_id)
                        clock_device.clock_half_period = n

                    elif self.devices.get_device(device_id).device_kind \
                            == self.devices.SIGGEN:
                        n = self.symbol.id

                        # Check if specified waveform is binary
                        for i in n:
                            if i in '10':
                                waveform_binary = True
                            else:
                                waveform_binary = False
                                break

                        if waveform_binary:
                            # Set siggen waveform
                            siggen_device = self.devices.get_device(device_id)
                            # Convert to string to allow for list comprehension
                            siggen_device.waveform = n

                        else:
                            self.scanner.display_error(
                                SemanticError, "Siggen can only take "
                                               "binary waveforms.")
                            return True

                    elif self.devices.get_device(device_id) is None:
                        self.scanner.display_error(
                            SemanticError, "Device doesn't exist.")
                        return True

                    else:
                        # Gates can only have 1-16 inputs
                        if n > 16:
                            self.scanner.display_error(
                                SemanticError, "Device can only "
                                               "have 1-16 inputs.")
                            return True

                        # Add all the inputs to the device..
                        else:
                            for input_num in range(1, n + 1):
                                [input_id] = self.devices.names.lookup(
                                    ["I"+str(input_num)])
                                self.devices.add_input(device_id, input_id)
                                self.devices.add_output(device_id, None)

            else:
                self.scanner.display_error(
                    SyntaxError, "Device parameter has not been specified.")
                return True

        if self.devices.get_device(device_id).device_kind \
                == self.devices.D_TYPE:
            device_error_type_name = 'DTYPE'

        else:
            device_error_type_name = 'XOR'

        self.symbol = self.scanner.get_symbol()

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type == self.scanner.SEMICOLON:
            pass

        elif self.symbol.type == self.scanner.NUMBER:
            self.scanner.display_error(
                SyntaxError, "Cannot specify inputs "
                             "for {}".format(device_error_type_name))
            return True

        elif self.symbol.type == self.scanner.CLOSE_SQUARE:
            self.scanner.display_error(
                SyntaxError, "Expected ';' to end device line.", "EOL")
            return False

        else:
            self.scanner.display_error(
                SyntaxError, "Expected ';' to end device line.")
            return True

        return True

    def parse_CONNECTIONS_section(self):
        """Parse the CONNECTIONS section device by device."""
        # CHECK for word device
        self.symbol = self.scanner.get_symbol(["}", "]", ""])

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type == self.scanner.CLOSE_SQUARE:
            device_names_to_check = self.list_of_connected_devices()
            for con_name in self.all_cons_list:
                if con_name in device_names_to_check:
                    device_names_to_check.pop(
                        device_names_to_check.index(con_name))

            undefined_connections = ', '.join(device_names_to_check)

            if device_names_to_check != []:
                self.scanner.display_error(

                    SemanticError, "The following device(s) do not have "
                                   "connections defined: %s" %
                                   undefined_connections)

            return False

        if self.symbol.type == self.scanner.EOF:
            return False

        elif self.symbol.id != self.scanner.DEVICE:
            self.scanner.display_error(
                SyntaxError, "List of connections must start "
                             "with the word 'device'.", ["}", "]", ""])
            return True

        # CHECK for device name
        self.symbol = self.scanner.get_symbol(["}", "]", ""])

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type == self.scanner.NAME:
            self.con_device = self.devices.get_device(self.symbol.id)
            con_device_name = self.names.get_name_string(self.symbol.id)

            if con_device_name in self.all_cons_list:
                self.scanner.display_error(
                    ConnectionError, "Connections for device '{}' already "
                                     "assigned.".format(con_device_name),
                                     ["}", "]", ""])
                return True

            if self.con_device is None:
                if con_device_name not in self.does_not_exist_list:

                    # Prevent showing follow on errors if device does not exist
                    self.does_not_exist_list.append(con_device_name)
                    self.scanner.display_error(
                        SemanticError, "Device '{}' does not exist."
                                       .format(con_device_name),
                                       ["}", "]", ""])
                    return True

            self.all_cons_list.append(con_device_name)
        else:
            self.scanner.display_error(
                SyntaxError, "Expected a device name after the "
                             "word 'device'.", ["}", "]", ""])
            return True

        # CHECK for opening curly bracket
        self.symbol = self.scanner.get_symbol(["}", "]", ""])

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type != self.scanner.OPEN_CURLY:
            self.scanner.display_error(
                SyntaxError, "Expected '{' after device name.", ["}", "]", ""])
            return True

        counter = 0

        # PARSE each line encompassed by curly brackets
        while self.parse_Connections_lines():
            counter += 1

        if self.con_device is None:
            pass

        elif counter != len(self.con_device.inputs):

            self.scanner.display_error(
                SemanticError, "Device {} has not had all inputs "
                               "defined".format(con_device_name))
            return True

        if self.square_instead_of_curly is True:
            return False
        return True

    def parse_MONITORS_section(self):
        """Parse the MONITORS section."""
        # GET next symbol (after OPEN_SQUARE)
        self.symbol = self.scanner.get_symbol()

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type == self.scanner.ALL:
            device_objects = self.list_of_connected_devices_objects()
            for device in device_objects:
                dev_type = self.devices.get_device(
                    device.device_id).device_kind
                # Q and QBAR outputs for DTYPE
                if dev_type == self.devices.D_TYPE:
                    self.monitors.make_monitor(
                        device.device_id, self.devices.Q_ID)
                    self.monitors.make_monitor(
                        device.device_id, self.devices.QBAR_ID)

                else:
                    self.monitors.make_monitor(
                        device.device_id, None)

            return True

        # CHECK for NAME
        if self.symbol.type == self.scanner.NAME:
            self.monitor_device = self.devices.get_device(self.symbol.id)
            monitor_device_name = self.names.get_name_string(self.symbol.id)
            if monitor_device_name in self.all_monitors_list:
                self.scanner.display_error(
                    SemanticError, "Device '{}' already assigned for "
                                   "monitoring.".format(monitor_device_name))
                return True

            self.all_monitors_list.append(monitor_device_name)

            # CHECK for ID error, if none, proceed to fetch device object
            if self.symbol.id is None:
                self.scanner.display_error(
                    SemanticError, "%s is not a valid "
                                   "device." % monitor_device_name)
                return True

            device = self.devices.get_device(self.symbol.id)
            name = self.scanner.names.get_name_string(self.symbol.id)

            # CHECK for device - get_device returns None for invalid device_id
            if device is None:
                if name not in self.does_not_exist_list:

                    self.scanner.display_error(
                        SemanticError, "%s is not a valid device." % name)
                    return True

            # Special case if NAME is DTYPE as can have .Q or .QBAR appended
            elif device.device_kind == self.devices.D_TYPE:
                # Track device_id here to create monitor later
                device_id = self.symbol.id

                # GET next symbol and CHECK it's DOT
                self.symbol = self.scanner.get_symbol()

                if self.scanner.error is True:
                    self.scanner.error = False
                    return True

                if self.symbol.type == self.scanner.DOT:
                    # Symbol following DTYPE and DOT must be Q or QBAR
                    self.symbol = self.scanner.get_symbol()
                    if self.scanner.error is True:
                        self.scanner.error = False
                        return True

                    if self.symbol.id in self.devices.dtype_output_ids:
                        # Make monitor for device with output..
                        self.monitors.make_monitor(device_id, self.symbol.id)

                    # Error if symbol after DOT is not Q or QBAR
                    else:
                        self.scanner.display_error(
                            SyntaxError, "DTYPE can only use .Q or .QBAR")
                        return True

                # Error for DTYPE not being followed by DOT
                else:
                    self.scanner.display_error(
                        SyntaxError, "DTYPE must be followed by .")
                    return True

            # For devices that are not DTYPE, make monitor with output_id None
            else:
                self.monitors.make_monitor(self.symbol.id, None)

                # USE self.monitors checks or keep with our own ones???

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

        return True

    def parse_Connections_lines(self):
        """Parse a CONNECTION line in a CONNECTION subsection."""
        self.square_instead_of_curly = False

        if self.symbol.type == self.scanner.CLOSE_CURLY:
            return False
        self.symbol = self.scanner.get_symbol()

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type == self.scanner.CLOSE_CURLY:
            return False

        if self.symbol.type == self.scanner.CLOSE_SQUARE:
            self.square_instead_of_curly = True
            self.scanner.display_error(
                SyntaxError, "Expected '}' to end connections subsection.")
            return False

        # CHECK for start connection
        elif self.symbol.type != self.scanner.NAME:
            self.scanner.display_error(
                ConnectionError, "Connection must start with a device name.")
            return True
        start_con = self.devices.get_device(self.symbol.id)
        start_con_name = self.names.get_name_string(self.symbol.id)

        if start_con is None:
            if start_con_name not in self.does_not_exist_list:
                self.does_not_exist_list.append(start_con_name)

                self.scanner.display_error(
                    SemanticError, "Device '{}' does not exist."
                                   .format(start_con_name))
                return True

        elif start_con.device_kind == self.devices.D_TYPE:
            self.symbol = self.scanner.get_symbol()
            if self.scanner.error is True:
                self.scanner.error = False
                return True

            if self.symbol.type != self.scanner.DOT:
                self.scanner.display_error(
                    SyntaxError, "Expected '.' after DTYPE name.")
                return True

            self.symbol = self.scanner.get_symbol()

            if self.scanner.error is True:
                self.scanner.error = False
                return True

            if self.symbol.id not in self.devices.dtype_output_ids:
                self.scanner.display_error(
                    SyntaxError, "Invalid DTYPE output name")
                return True

            start_con_port_id = self.symbol.id

        else:
            start_con_port_id = None

        # CHECK for arrow
        self.symbol = self.scanner.get_symbol()

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type != self.scanner.ARROW:
            self.scanner.display_error(
                ConnectionError, "Expected '->' inbetween "
                                 "start and end connections.")
            return True

        # CHECK for end connection
        self.symbol = self.scanner.get_symbol()

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type != self.scanner.NAME:
            self.scanner.display_error(
                SyntaxError, "A device name must follow "
                             "the connection arrow.")
            return True

        end_con = self.devices.get_device(self.symbol.id)
        end_con_name = self.names.get_name_string(self.symbol.id)

        if end_con is None:
            if end_con_name not in self.does_not_exist_list:
                self.does_not_exist_list.append(end_con_name)

                self.scanner.display_error(
                    SemanticError, "Device '{}' does not exist."
                                   .format(end_con_name))
                return True

        elif end_con != self.con_device:
            self.scanner.display_error(
                ConnectionError, "This connection has been listsed under the "
                                 "incorrect device \nsubsection.")

            return True

        self.symbol = self.scanner.get_symbol()

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type != self.scanner.DOT:
            self.scanner.display_error(
                SyntaxError, "Expected '.' after device name")
            return True

        self.symbol = self.scanner.get_symbol()

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type != self.scanner.NAME:
            self.scanner.display_error(
                SyntaxError, "Invalid port name.")
            return True
        end_con_port_id = self.symbol.id

        # Only attempt to make network if total error count is 0
        if self.scanner.error_count == 0:
            con_status = self.network.make_connection(
                         start_con.device_id, start_con_port_id,
                         end_con.device_id, end_con_port_id)
            if con_status == self.network.INPUT_CONNECTED:
                self.scanner.display_error(
                    ConnectionError, "{}.{} is already connected.".format(
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

        if self.scanner.error is True:
            self.scanner.error = False
            return True

        if self.symbol.type == self.scanner.SEMICOLON:
            pass

        elif self.symbol.type == self.scanner.CLOSE_CURLY:
            self.scanner.display_error(
                SyntaxError, "Expected ';' to end connection line.")
            return False

        else:
            self.scanner.display_error(
                SyntaxError, "Expected ';' to end connection line.")
            return True

        return True

    def list_of_connected_devices(self):
        """Generate a list of devices.

        Devices need to have connections defined in the CONNECTIONS
        section.
        """
        device_names_to_check = []
        # CHECK all DEVICES have CONNECTIONS defined

        device_ids = self.names.lookup(self.all_devices_list)
        check_device_ids = []
        for check_id in device_ids:
            if self.devices.get_device(check_id) is not None:
                check_device_kind = \
                    self.devices.get_device(check_id).device_kind
                if check_device_kind != self.devices.SWITCH and \
                        check_device_kind != self.devices.CLOCK and\
                        check_device_kind != self.devices.SIGGEN:
                    check_name = self.names.get_name_string(check_id)
                    device_names_to_check.append(check_name)

        return device_names_to_check

    def list_of_connected_devices_objects(self):
        """Generate a list of made device objects."""
        device_object_list = []

        device_ids = self.names.lookup(self.all_devices_list)
        for device_id in device_ids:
            if self.devices.get_device(device_id) is not None:
                device_object = self.devices.get_device(device_id)
                device_object_list.append(device_object)

        return device_object_list
