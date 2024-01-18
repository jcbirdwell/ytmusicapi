"""models for oauth authentication"""

from abc import ABC, abstractmethod
from typing import Literal, Mapping, TypedDict, Union

DefaultScope = Union[str, Literal["https://www.googleapis.com/auth/youtube"]]
Bearer = Union[str, Literal["Bearer"]]


class BaseTokenDict(TypedDict):
    """Limited token. Does not provide a refresh token. Commonly obtained via a token refresh."""

    access_token: str  #: str to be used in Authorization header
    scope: DefaultScope  #: should be 'https://www.googleapis.com/auth/youtube'
    token_type: Bearer  #: should be 'Bearer'


class APITokenDict(BaseTokenDict):
    expires_in: int  #: seconds until expiration from request timestamp


class RefreshableTokenDict(BaseTokenDict):
    """Entire token. Including refresh. Obtained through token setup."""

    expires_at: int  #: UNIX epoch timestamp in seconds
    refresh_token: str  #: str used to obtain new access token upon expiration


class AuthCodeDict(TypedDict):
    """Keys for the json object obtained via code response during auth flow."""

    device_code: str  #: code obtained via user confirmation and oauth consent
    user_code: str  #: alphanumeric code user is prompted to enter as confirmation. formatted as XXX-XXX-XXX.
    expires_in: int  #: seconds from original request timestamp
    interval: int  #: (?) "5" (?)
    verification_url: str  #: base url for OAuth consent screen for user signin/confirmation


class Credentials(ABC):
    """Base class representation of YouTubeMusicAPI OAuth Credentials"""

    client_id: str
    client_secret: str

    @abstractmethod
    def get_code(self) -> Mapping:
        raise NotImplementedError()

    @abstractmethod
    def token_from_code(self, device_code: str) -> RefreshableTokenDict:
        raise NotImplementedError()

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> APITokenDict:
        raise NotImplementedError()
