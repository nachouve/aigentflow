import logging

logger = logging.getLogger(__name__)


def decode_output(byte_string, encodings=None):
    """
    Attempt to decode a byte string using multiple encodings
    """
    if encodings is None:
        encodings = ["utf-8", "cp1252", "latin-1"]

    if not byte_string:
        return ""

    for encoding in encodings:
        try:
            return byte_string.decode(encoding)
        except UnicodeDecodeError:
            logger.debug(f"Failed to decode with {encoding}")
            continue

    return byte_string.decode("latin-1")
