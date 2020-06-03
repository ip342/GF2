"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
from errors import *


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

        # Create list of each file line
        self.file_as_list = [line.rstrip('\n') for line in open(path, 'r')]

        # Initialise symbol types
        self.names = names
        self.symbol_type_list = [self.HEADER, self.KEYWORD, self.NAME,
                                 self.NUMBER, self.EQUALS, self.COMMA,
                                 self.OPEN_SQUARE, self.CLOSE_SQUARE,
                                 self.SLASH, self.SEMICOLON, self.ARROW,
                                 self.DOT, self.OPEN_CURLY, self.CLOSE_CURLY,
                                 self.ALL, self.EOF] = range(16)

        # Creat symbol IDs for headers
        self.header_list = ['DEVICES', 'CONNECTIONS', 'MONITORS']
        [self.DEVICES_ID, self.CONNECTIONS_ID, self.MONITORS_ID] = \
            self.names.lookup(self.header_list)

        # Create symbol IDs for keywords
        self.keyword_list = ['cycle', 'cycles', 'input', 'inputs', 'device']

        [self.CYCLE, self.CYCLES, self.INPUT, self.INPUTS, self.DEVICE] = \
            self.names.lookup(self.keyword_list)

        self.end_characters = [';', '}', ']', '']
        self.monitor_all = ['all']

        self.current_character = ' '
        self.current_line = 0
        self.current_character_number = 0
        self.error_count = 0
        self.error_list = []
        self.error = False

    def get_symbol(self, stop=None):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()

        # go to current non whitespace character
        self.skip_spaces()

        # First check if in comment
        # ignore multi line comments
        if self.current_character == '#':
            self.advance()
            while self.current_character != '#':
                self.advance()

                if self.current_character == '':
                    self.display_error(
                        CommentError,
                        _('Expected # at the end of multi-line comment'), stop)
                    symbol.type = self.EOF
                    break

            self.advance()
            self.skip_spaces()

        # ignore single line comments
        if self.current_character == '/':
            self.advance()
            if self.current_character == '/':
                while self.current_character != '\n':
                    self.advance()

            else:
                self.display_error(
                    CommentError, _("Expected '/' after '/' to "
                                  "indicate comment"), stop)
                self.error = True

            self.advance()
            self.skip_spaces()

        # Now check for symbol type

        # words
        if self.current_character.isalpha():
            name_string = self.get_name()[0]
            if name_string.upper() in self.header_list:
                symbol.type = self.HEADER

                symbol.id = self.names.query(name_string.upper())
            elif name_string.lower() in self.keyword_list:
                symbol.type = self.KEYWORD
                symbol.id = self.names.query(name_string.lower())

            elif name_string.lower() in self.monitor_all:
                symbol.type = self.ALL

            else:
                symbol.type = self.NAME
                [symbol.id] = self.names.lookup([name_string])

        # numbers
        elif self.current_character.isdigit():
            symbol.type = self.NUMBER
            symbol.id = self.get_number()[0]

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
                self.display_error(
                    ArrowError, _("Unexpected character, expected "
                                "'>' after '-'"), stop)
                self.error = True

        elif self.current_character == '>':
            self.advance()
            self.display_error(
                ArrowError, _("Unexpected character, '>' must follow '-'"), stop)
            self.error = True

        elif self.current_character == '.':
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == '{':
            symbol.type = self.OPEN_CURLY
            self.advance()

        elif self.current_character == '}':
            symbol.type = self.CLOSE_CURLY
            self.advance()

        # end of file
        elif self.current_character == '':
            symbol.type = self.EOF

        # invalid character
        else:
            self.advance()
            self.display_error(SyntaxError, _('Invalid character'), stop)
            self.error = True

        return symbol

    def skip_spaces(self):
        """ Advance until non space symbol is encountered """

        while self.current_character.isspace():
            self.current_character = self.advance()

    def advance(self):
        """ Advance to next character """

        # first check if on new line

        if self.current_character == '\n':
            self.current_line += 1
            self.current_character_number = 0

        # check if on tab (only applies to certain text editors)

        if self.current_character == '\t':
            while (self.current_character_number % 4) != 0:
                self.current_character_number += 1

        # now read next character in definition file
        self.current_character = self.input_file.read(1)
        self.current_character_number += 1

        return self.current_character

    def get_name(self):
        """" When current character is a letter, return whole word """

        name = self.current_character

        while True:
            self.current_character = self.advance()
            if self.current_character.isalnum():
                name = name + self.current_character
            else:
                return [name, self.current_character]

    def get_number(self):
        """ When current character is a number, return whole number """

        number = self.current_character

        while True:
            self.current_character = self.advance()
            if self.current_character.isdigit():
                number = number + self.current_character
            else:
                return [number, self.current_character]

    def display_error(self, error_type, error_message='', stop=None):
        """ Error function to be called every time an error is found.
        Raises the error only in test mode, otherwise uses the Error class
        in errors.py to print the error. Error recovery is handled by
        advancing until specified stopping symbols. """

        self.error_count += 1

        # Only raise the error for filenames starting with 'test'
        if 'test' in sys.argv[0].lower():
            raise error_type

        else:
            try:
                self.errors = Error(error_type, error_message, self.current_line,
                            self.file_as_list[self.current_line],
                            self.current_character_number)
        
                self.error_list.append(self.errors.error_message)
            # In case of blank lines at end of file being stripped by rstrip method 
            except IndexError:
                self.errors = Error(error_type, error_message, self.current_line,
                            self.file_as_list[-1],
                            self.current_character_number)
        
                self.error_list.append(self.errors.error_message)

        # Comment error special case
        if error_type == CommentError:
            self.advance()
            while self.current_character != '\n':
                self.advance()
                if self.current_character == '':
                    break

        # Error recovery
        elif stop == "EOL":
            self.advance()

        elif self.current_character == '\n':
            self.advance()

        elif self.current_character in self.end_characters:
            self.advance()

        else:

            while True:
                self.advance()
                if stop is not None:
                    if self.current_character in stop:
                        # Advances past new line symbol
                        self.advance()
                        break
                elif self.current_character == ';':
                    # Advances past new line symbol
                    self.advance()
                    break
                elif self.current_character in self.end_characters:
                    break
