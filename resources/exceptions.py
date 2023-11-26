class ErrorHTMLMessageException(Exception):

    def __init__(self, message="It wasn't possible to continue due "
                               "to message error in the HTML."):
        self.message = message
        super().__init__(self.message)


class CloudFareException(Exception):
    def __init__(self, message="Cloudflare's validation is required. "
                               "'Checking if the site connection is secure'."):
        self.message = message
        super().__init__(self.message)


class LoginFailed(Exception):
    def __init__(self, message="The attempt to log in has failed"):
        self.message = message
        super().__init__(self.message)
