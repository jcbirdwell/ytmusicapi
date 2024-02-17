from ytmusicapi.auth.types import AuthType


class TestAuthTypes:
    def test_is_oauth(self, config):
        assert AuthType.is_oauth(config["auth"]["oauth_token"])
        assert not AuthType.is_oauth(config["auth"]["headers_raw"])

    def test_is_browser(self, config):
        assert AuthType.is_browser(config["auth"]["headers_raw"])
        assert not AuthType.is_browser(config["auth"]["oauth_token"])
