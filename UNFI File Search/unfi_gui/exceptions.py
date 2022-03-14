
class ViewRequiredException(Exception):
    """
    Raised when a frame is required but not found.
    """
    def __init__(self, message=None):
        if not message:
            message = "No frames have been registered."
        super().__init__(message)


class UnfiApiClientNotSetException(Exception):
    """
    Raised when a client is required but not found.
    """
    def __init__(self, message=None):
        if not message:
            message = "UnfiApiClient is required but not found."
    
        super().__init__(message)