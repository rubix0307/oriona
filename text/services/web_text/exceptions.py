from typing import Optional


class ApiError(Exception):
    def __init__(self, code: int, desc: Optional[str] = None):
        self.code = code
        self.desc = desc or 'API error'
        super().__init__(f'API error {code}: {self.desc}')

class WebTextError(Exception):
    pass

class WebTextResponceError(WebTextError):
    pass

class WebTextHttpError(WebTextError):
    pass

class WebTextTimeoutError(WebTextError, TimeoutError):
    pass


ERROR_HINTS = {
    110: 'Missing text to check',
    111: 'The text to check is empty',
    112: 'The text to check is too short',
    113: 'The text to check is too long',
    120: 'Missing user key',
    121: 'User key is empty',
    140: 'Server access error',
    141: 'Nonexistent user key',
    142: 'Insufficient symbols balance',
    143: 'Error while sending parameters',
    144: 'Server error',
    145: 'Server error',
    146: 'Access restricted',
    150: 'No shingles found. The text may be too short',
    151: 'Server error',
    160: 'Missing text uid',
    161: 'Uid is empty',
    170: 'Missing user key',
    171: 'User key is empty',
    180: 'Key–uid pair not found in the database',
    181: 'The text has not been checked yet',
    182: 'Text checked with errors. The money will be refunded',
    183: 'Server error',
    429: 'Rate limit exceeded',
}