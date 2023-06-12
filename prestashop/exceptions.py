# -*- coding: utf-8 -*-

class PrestaShopError(Exception):
    """Generic PrestaShop WebServices error class.
    """

    def __init__(self, msg, error_code=None,
                 ps_error_msg='', ps_error_code=None):
        """Intiliaze webservice error."""
        self.msg = msg
        self.error_code = error_code
        self.ps_error_msg = ps_error_msg
        self.ps_error_code = ps_error_code

    def __str__(self):
        """Include custom msg."""
        return repr(self.ps_error_msg or self.msg)


class PrestaShopAuthenticationError(PrestaShopError):
    """Authentication Exception

    Args:
        PrestaShopError (Unauthorized)
    """
