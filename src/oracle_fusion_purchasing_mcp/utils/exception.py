class ConfigurationError(Exception):
    """Raised when Oracle Fusion Env Variable configuration is invalid."""
    pass

class OracleAPIError(Exception):
    """An error occurred while communicating with Oracle Fusion"""
    pass

class OracleJSONDecodeError(Exception):
    """An Error occurred while parsing the API JSON response"""
    pass
