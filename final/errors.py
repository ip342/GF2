"""Used in the Logic Simulator project to provide information to the user when
errors occurin the definition file to allow them to understand where the error
is and why it occurs. The error type is returned, along with the location and a
short message describing the error.

Classes:
-------
Error - base error class function which prints error type, the line which the
error occurs at, a carat pointing to the character at which the error occurs,
and a short message describing the error.

SemanticError
CommentError
ArrowError
NetworkError
ConnectionError
"""

import sys


class Error(Exception):
    """ Base error class function which prints error type, the line which the
    error occurs, a carat pointing to the character at which the error occurs
    and a short message describing the error.

    Parameters
    ----------
    error_type: type of error.
    message: messsage describing the error.
    line_number: file line number which error occured on.
    line: full printed line which error occured on.
    character: character number which error occured on.

    Public methods
    -------------
    No public methods.
    """

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

        self.error_message = ('\n' + _('Line number ') + str(line_number + 1)
                              + _(', Character ') + str(character - 1) + '\n'
                              + line + '\n' + (character - 2)*' ' + '^' + '\n'
                              + error_class + ': ' + str(message) + '\n\n' +
                              '*' * 76)


# Specific error classes for accurate pytests
class SemanticError(Exception):
    """ Semantic error class """
    pass


class CommentError(Exception):
    """ Comment error class """
    pass


class ArrowError(Exception):
    """ Arrow error class """
    pass


class NetworkError(Exception):
    """ Network error class """
    pass


class ConnectionError(Exception):
    """ Connection error class """
    pass
