"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""

        # Open file
        try:
            self.input_file = open(path, 'r')
        except FileNotFoundError:
            raise FileNotFoundError('Error: No such file in current directory')
            sys.exit()
            
        # Remove blank lines, store file in list of each line
        self.file_as_list = []
        with self.input_file as file:
            for line in file:
                line = line.strip()
                if line:
                    self.file_as_list.append(line)
        
        # Initialise symbol types
        self.names = names
        self.symbol_list = [self.HEADER, self.PARAMETER, self.NAME, self.EQUALS, self.COMMA, self.OPEN_SQUARE, self.CLOSE_SQUARE, self.EQUALS, self.SEMICOLON, self.ARROW, self.DOT, self.OPEN_CURLY, self.CLOSE_CURLY, self.HASH, self.EOF]

        self.header_list = ['DEVICES', 'CONNECTIONS', 'MONITOR']
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITOR_ID] = self.names.lookup(self.header_list)

        self.parameter_list = ['cycle', 'cycles', 'input', 'inputs']
        [self.CYCLE, self.CYCLES, self.INPUT, self.INPUTS] = self.names.lookup(self.parameter_list)
        
        self.device = ['device']
        [self.DEVICE] = self.names.lookup(self.device)
        
        self.end_symbols = [self.SEMICOLON, self.CLOSE_CURLY, self.CLOSE_SQUARE, self.EOF]

        self.current_character = ''
        self.current_line = 0
        self.current_character_number = 0

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
