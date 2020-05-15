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
        self.symbol_type_list = [self.HEADER, self.KEYWORD, self.NAME, self.EQUALS, self.COMMA, self.OPEN_SQUARE,
        self.CLOSE_SQUARE, self.SEMICOLON, self.ARROW, self.DOT, self.OPEN_CURLY, self.CLOSE_CURLY, self.HASH, self.EOF] = range(14)

        self.header_list = ['DEVICES', 'CONNECTIONS', 'MONITORS']
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITORS_ID] = self.names.lookup(self.header_list)

        self.keyword_list = ['cycle', 'cycles', 'input', 'inputs', 'device']
        [self.CYCLE, self.CYCLES, self.INPUT, self.INPUTS, self.DEVICE] = self.names.lookup(self.parameter_list)

        self.end_symbols = [self.SEMICOLON, self.CLOSE_CURLY, self.CLOSE_SQUARE, self.EOF]

        self.current_character = ''
        self.current_line = 0
        self.current_character_number = 0

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""

        symbol = Symbol()
        # Go to current non whitespace character
        self.skip_spaces()

        # words
        if self.current_character.isalpha():
            name_string = self.get_name()
            if name_string.upper() in self.header_list:
                symbol.type = self.HEADER
                symbol.id = self.names.query(self.name_string.upper())
            elif name_string.lower() in self.keyword_list:
                symbol.type = self.KEYWORD
                symbol.id = self.names.query(self.name_string.lower())
            else:
                symbol.type = self.NAME
                symbol.id = self.names.query(self.name_string)
                
         #   return (self.name_string + ' ') not sure if line is required

        # numbers
        elif self.current_character.isdigit():
            symbol.type = self.NUMBER
            symbol.id = self.get_number()
            
         #   return (symbol.id[0] + ' ') not sure if line is required

        # punctuation
        elif self.current_character == '=':
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ',':
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == '[':
            symbol.type = self.OPEN_SQUARE
            self.advance()

        elif self.current_character == ']':
            symbol.type = self.CLOSE_SQUARE
            self.advance()
            
        elif self.current_character == ';':
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == '-':
            if self.advance() == '>':
                symbol.type = self.ARROW
                self.advance()
            else:
                self.error(SyntaxError, 'Unexpected character, expected '>' after '-'')

        elif self.current_character == '.':
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == '{':
            symbol.type = self.OPEN_CURLY
            self.advance()

        elif self.current_character == '}':
            symbol.type = self.CLOSE_CURLY
            self.advance()

        # comments 
        elif self.current_character == '#':
            symbol.type = self.HASH
            self.advance()
            
            while self.current_character =! '#':
                self.advance()

                if self.current_character == '':
                    self.error(SyntaxError, 'Expected # at the end of comment')
                    
            self.advance()
            
        elif self.current_character == '/':
            self.advance()
            if self.current_character == '/':
                symbol.type = self.EOF
            else:
                self.error(SyntaxError, 'Expected '/' after '/' to indicate End of File')
                
        else:
            self.error(SyntaxError, 'Invalid character')

        return symbol 

    def skip_spaces(self):
        
    def advance(self):
        
    def get_name(self):
        
        """" When current character is a letter, return whole word """

        name = self.current_character

        while True:
            self.current_character = self.advance()
            if self.current_character.isalnum():
                name = name + self.current_character 
            else:
                return name

    def get_number(self):
        
        """ When current character is a number, return whole number """

        number = self.current_character

        while True:
            self.current_character = self.advance()
            if self.current_character.isdigit():
                number = number + self.current_character 
            else:
                return number 




























                
        
            
