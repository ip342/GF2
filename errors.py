"""Used in the Logic Simulator project to define various errors which may occur
in the definition file. The error type is returned, along with the location
and a short message describing the error.
Classes
-------
Error - Base error class
SemanticError
SyntaxError
"""

import sys


class Error(Exception):
    def __init__(self, error_class, message, line_number, line, character):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.error_type = error_class
        self.message = message

        if error_class == SemanticError:
            error_type = 'SemanticError'

        if error_class == SyntaxError:
            error_type = 'SyntaxError'

        if error_class == CommentError:
            error_type = 'SyntaxError'

        print('*'*50 + '\n' + 'Line number ' + str(line_number + 1) + ', Character ' + str(character) + '\n'
            + line + '\n' + (character - 2)*' ' + '^' + '\n'
            + error_type +': ' + str(message))


class SemanticError(Exception):
    pass


class SyntaxError(Exception):
    pass


class CommentError(Exception):
    pass
