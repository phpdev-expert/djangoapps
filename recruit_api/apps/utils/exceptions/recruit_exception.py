class RecruitException(Exception):
    def __init__(self, message, errors=None):
        """
        :param message: Sets the message of the exception.
        :param errors: Sets the custom errors if you want any.
        """
        self.message = message
        # Call the base class constructor with the parameters it needs
        super().__init__(self.message)
        self.errors = errors
