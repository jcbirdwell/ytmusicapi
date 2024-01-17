"""enum representing types of authentication supported by this library"""

from enum import Enum, auto
from typing import List

from requests.structures import CaseInsensitiveDict


class AuthType(int, Enum):
    """enum representing types of authentication supported by this library"""

    @classmethod
    def is_oauth(cls, headers: CaseInsensitiveDict) -> bool:
        oauth_structure = {
            "access_token",
            "expires_at",
            "token_type",
            "refresh_token",
        }
        return all(key in headers for key in oauth_structure)

    UNAUTHORIZED = auto()

    BROWSER = auto()

    #: client auth via OAuth token refreshing
    OAUTH_DEFAULT = auto()

    #: YTM instance is using a non-default OAuth client (id & secret)
    OAUTH_CUSTOM_CLIENT = auto()

    #: allows fully formed OAuth headers to ignore browser auth refresh flow
    OAUTH_CUSTOM_FULL = auto()

    @classmethod
    def oauth_types(cls) -> List["AuthType"]:
        return [cls.OAUTH_DEFAULT, cls.OAUTH_CUSTOM_CLIENT, cls.OAUTH_CUSTOM_FULL]
