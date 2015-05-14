class CLIException(Exception):
    pass


class ConfigNotFound(Exception):
    pass


class UnknownCommand(CLIException):
    pass


class HostConfigError(CLIException):
    pass


class InvalidPath(CLIException):
    pass
