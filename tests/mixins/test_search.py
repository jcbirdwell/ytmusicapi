import pytest


class TestSearch:
    def test_search_exceptions(self, yt_auth):
        query = "edm playlist"
        with pytest.raises(Exception, match="Invalid filter provided"):
            yt_auth.search(query, only="song")
        with pytest.raises(Exception, match="Invalid scope provided"):
            yt_auth.search(query, scope="upload")

    @pytest.mark.parametrize("query", ["Monekes", "qllwlwl", "heun"])
    def test_search_queries(self, yt, yt_brand, query: str) -> None:
        results = yt_brand.search(query)
        assert ["result_type" in r for r in results] == [True] * len(results)
        assert len(results) >= 10
        results = yt.search(query)
        assert len(results) >= 10

    def test_search_ignore_spelling(self, yt_auth):
        results = yt_auth.search("Martin Stig Andersen - Deteriation", ignore_spelling=True)
        assert len(results) > 0

    def test_search_filters(self, yt_auth):
        query = "hip hop playlist"
        results = yt_auth.search(query, only="songs")
        assert len(results) > 10
        assert all(item["result_type"] == "song" for item in results)
        results = yt_auth.search(query, only="videos")
        assert len(results) > 10
        assert all(item["result_type"] == "video" for item in results)
        results = yt_auth.search(query, only="albums", limit=40)
        assert len(results) > 20
        assert all(item["result_type"] == "album" for item in results)
        results = yt_auth.search("armen van buren", only="artists", ignore_spelling=True)
        assert len(results) < 5
        assert all(item["result_type"] == "artist" for item in results)
        results = yt_auth.search("classical music", only="playlists")
        assert len(results) > 10
        assert all(item["result_type"] == "playlist" for item in results)
        results = yt_auth.search("clasical music", only="playlists", ignore_spelling=True)
        assert len(results) > 10
        results = yt_auth.search("clasic rock", only="community_playlists", ignore_spelling=True)
        assert len(results) > 10
        assert all(item["result_type"] == "playlist" for item in results)
        results = yt_auth.search("hip hop", only="featured_playlists")
        assert len(results) > 10
        assert all(item["result_type"] == "playlist" for item in results)
        results = yt_auth.search("some user", only="profiles")
        assert len(results) > 10
        assert all(item["result_type"] == "profile" for item in results)
        results = yt_auth.search(query, only="podcasts")
        assert len(results) > 10
        assert all(item["result_type"] == "podcast" for item in results)
        results = yt_auth.search(query, only="episodes")
        assert len(results) > 10
        assert all(item["result_type"] == "episode" for item in results)

    def test_search_uploads(self, config, yt, yt_oauth):
        with pytest.raises(Exception, match="No filter can be set when searching uploads"):
            yt.search(
                config["queries"]["uploads_songs"],
                only="songs",
                scope="uploads",
                limit=40,
            )
        results = yt_oauth.search(config["queries"]["uploads_songs"], scope="uploads", limit=40)
        assert len(results) > 20

    def test_search_library(self, config, yt_oauth):
        results = yt_oauth.search(config["queries"]["library_any"], scope="library")
        assert len(results) > 5
        results = yt_oauth.search(config["queries"]["library_songs"], only="songs", scope="library", limit=40)
        assert len(results) > 10
        results = yt_oauth.search(
            config["queries"]["library_albums"], only="albums", scope="library", limit=40
        )
        assert len(results) >= 4
        results = yt_oauth.search(
            config["queries"]["library_artists"], only="artists", scope="library", limit=40
        )
        assert len(results) >= 1
        results = yt_oauth.search(config["queries"]["library_playlists"], only="playlists", scope="library")
        assert len(results) >= 1
        with pytest.raises(Exception):
            yt_oauth.search("beatles", only="community_playlists", scope="library", limit=40)
        with pytest.raises(Exception):
            yt_oauth.search("beatles", only="featured_playlists", scope="library", limit=40)
