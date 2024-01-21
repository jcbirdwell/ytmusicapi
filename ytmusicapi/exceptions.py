class APIException(Exception):
    """Error response from youtube api"""


class WrongAuthType(Exception):
    """Function call unavailable with current authentication type"""
