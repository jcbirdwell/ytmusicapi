import configparser
from pathlib import Path

import pytest

from ytmusicapi import YTMusic


def get_resource(file: str) -> str:
    data_dir = Path(__file__).parent
    return data_dir.joinpath(file).as_posix()


@pytest.fixture(name="config")
def fixture_config() -> configparser.RawConfigParser:
    config = configparser.RawConfigParser()
    config.read(get_resource("test.cfg"), "utf-8")
    return config


@pytest.fixture(name="sample_album")
def fixture_sample_album() -> str:
    """Eminem - Revival"""
    return "MPREb_4pL8gzRtw1p"


@pytest.fixture(name="sample_video")
def fixture_sample_video() -> str:
    """Oasis - Wonderwall"""
    return "hpSrLjc5SMs"


@pytest.fixture(name="liked_song_id")
def fixture_liked_song_id(config) -> str:
    """
    A video_id of a track in oauth account's liked songs
                ** with one artist **
    """
    return config["liked"]["video_id"]


@pytest.fixture(name="liked_song_artist_id")
def fixture_liked_song_artist_id(config) -> str:
    """The artist_id of a liked track"""
    return config["liked"]["artist_id"]


@pytest.fixture(name="sample_playlist")
def fixture_sample_playlist() -> str:
    """very large playlist"""
    return "PL6bPxvf5dW5clc3y9wAoslzqUrmkZ5c-u"


@pytest.fixture(name="browser_filepath")
def fixture_browser_filepath(config) -> str:
    return get_resource(config["auth"]["browser_file"])


@pytest.fixture(name="oauth_filepath")
def fixture_oauth_filepath(config) -> str:
    return get_resource(config["auth"]["oauth_file"])


@pytest.fixture(name="yt")
def fixture_yt() -> YTMusic:
    return YTMusic()


@pytest.fixture(name="yt_auth")
def fixture_yt_auth(browser_filepath) -> YTMusic:
    """a non-brand account that is able to create uploads"""
    return YTMusic(browser_filepath, location="GB")


@pytest.fixture(name="yt_oauth")
def fixture_yt_oauth(oauth_filepath) -> YTMusic:
    return YTMusic(oauth_filepath)


@pytest.fixture(name="yt_brand")
def fixture_yt_brand(config) -> YTMusic:
    return YTMusic(config["auth"]["headers"], config["auth"]["brand_account"])


@pytest.fixture(name="yt_empty")
def fixture_yt_empty(config) -> YTMusic:
    return YTMusic(config["auth"]["headers_empty"], config["auth"]["brand_account_empty"])
