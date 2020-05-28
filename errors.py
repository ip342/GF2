"""Used in the Logic Simulator project to provide information to the user when
errors occurin the definition file to allow them to understand where the error
is and why it occurs. The error type is returned, along with the location and a
short message describing the error.

Classes
-------
Error - Base error class function which prints error type, the line which the
error occurs at, a carat pointing to the character at which the error occurs,
and a short message describing the error.

SemanticError
CommentError
"""

import sys

# Main error class


class Error(Exception):
    def __init__(self, error_type, message, line_number, line, character):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.error_type = error_type
        self.message = message

        # Error classes grouped for printed error message
        Semantic = [SemanticError]
        Syntax = [SyntaxError, CommentError, ArrowError]

        if error_type in Semantic:
            error_class = 'SemanticError'

        elif error_type in Syntax:
            error_class = 'SyntaxError'

        elif error_type == NetworkError:
            error_class = 'NetworkError'

        elif error_type == ConnectionError:
            error_class = 'ConnectionError'

        print('*'*50 + '\n' + 'Line number ' + str(line_number + 1) + 
              ', Character ' + str(character - 1) + '\n'
              + line + '\n' + (character - 2)*' ' + '^' + '\n'
              + error_class + ': ' + str(message))


# Specific error classes for accurate pytests
class SemanticError(Exception):
    pass


class CommentError(Exception):
    pass


class ArrowError(Exception):
    pass


class NetworkError(Exception):
    pass


class ConnectionError(Exception):
    pass
