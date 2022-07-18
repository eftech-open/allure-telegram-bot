class HttpResponseErrors(Exception):
    """
    Error codes in the response
    """
    def __init__(self, expected_code, status_code):
        self.expected_code = expected_code
        self.status_code = status_code
        super().__init__()

    def __str__(self):
        return f"Expected status code [{self.expected_code}] not equals [{self.status_code}]"
