import warnings

import pytest


class TestBrowsing:
    def test_get_artist(self, yt, yt_oauth, liked_song_artist_id):
        # test handling of non-implemented sections by parser.append_channel_contents
        yt_oauth.get_artist(liked_song_artist_id)

        # Wet Baes; artist with no extensions on albums/singles
        artist = yt.get_artist("UCB-qDrhpXQanKPPSu9GKLQA")
        assert "artist_id" in artist
        # ensure artist songs are being correctly parsed
        targ = next((x for x in artist["songs"]["items"] if x["video_id"] == "ZZZ26yeKsnA"), None)
        assert targ is not None
        assert targ["album"]["id"] is not None

        artist = yt.get_artist("MPLAUCmMUZbaYdNH0bEd1PAlAqsA")
        assert len(artist) == 17

        # make sure artists are correctly filled for categories
        for k in ["songs", "videos"]:
            assert {"id": "UCmMUZbaYdNH0bEd1PAlAqsA", "name": "Oasis"} in artist[k]["items"][0]["artists"]
        single = artist["singles"]["items"][0]
        assert len(single["year"]) == 4 and single["year"].isnumeric()
        assert single["type"] == "Single"

        # test correctness of related artists
        related = artist["related"]["items"]
        assert len(
            [x for x in related if set(x.keys()) == {"browse_id", "name", "thumbnails", "sub_count"}]
        ) == len(related)

        artist = yt.get_artist("UCLZ7tlKC06ResyDmEStSrOw")  # no album year
        assert len(artist) >= 11

    def test_get_artist_albums(self, yt):
        artist = yt.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = yt.get_artist_albums(artist["albums"]["ext"])
        assert len(results) == 100
        results = yt.get_artist_albums(artist["singles"]["ext"])
        assert len(results) == 100

        results_unsorted = yt.get_artist_albums(artist["albums"]["ext"], limit=None)
        assert len(results_unsorted) >= 300

        results_sorted = yt.get_artist_albums(artist["albums"]["ext"], limit=None, order="alphabetical order")
        assert len(results_sorted) >= 300
        assert results_sorted != results_unsorted

        with pytest.raises(ValueError, match="Invalid order"):
            yt.get_artist_albums(artist["albums"]["ext"], order="order")

    def test_get_user(self, yt):
        results = yt.get_user("UC44hbeRoCZVVMVg5z0FfIww")
        assert len(results) == 4

    def test_get_user_playlists(self, yt, yt_auth):
        user = yt_auth.get_user("UCPVhZsC2od1xjGhgEc2NEPQ")  # VEVO playlists
        results = yt_auth.get_user_playlists(user["playlists"]["ext"])
        assert len(results) > 100

        results_empty = yt.get_user_playlists(user["playlists"]["ext"])
        assert len(results_empty) == 0

    def test_get_home(self, yt, yt_auth):
        result = yt.get_home(limit=6)
        assert len(result) >= 6
        result = yt_auth.get_home(limit=15)
        assert len(result) >= 15

    def test_get_album_browse_id(self, yt, sample_album):
        warnings.filterwarnings(action="ignore", category=DeprecationWarning)
        browse_id = yt.get_album_browse_id("OLAK5uy_nMr9h2VlS-2PULNz3M3XVXQj_P3C2bqaY")
        assert browse_id == sample_album

    def test_get_album_browse_id_issue_470(self, yt):
        escaped_browse_id = yt.get_album_browse_id("OLAK5uy_nbMYyrfeg5ZgknoOsOGBL268hGxtcbnDM")
        assert escaped_browse_id == "MPREb_scJdtUCpPE2"

    def test_get_album(self, yt, yt_auth, sample_album):
        album = yt_auth.get_album(sample_album)
        assert album["browse_id"] == sample_album
        assert album["name"] == "Revival"
        assert len(album) >= 9
        assert "explicit" in album
        assert album["tracks"][0]["explicit"]

        # assert all(item["views"] is not None for item in album["tracks"])
        assert album["tracks"][0]["track_number"] == 1
        assert "feedback_tokens" in album["tracks"][0]
        album = yt.get_album("MPREb_BQZvl3BFGay")
        assert len(album["tracks"]) == 7
        assert len(album["tracks"][0]["artists"]) == 1
        album = yt.get_album("MPREb_rqH94Zr3NN0")
        assert len(album["tracks"][0]["artists"]) == 2

        album_id = "MPREb_ObbUYP3Kjuy"  # Notion EP - Tash Sultana
        album = yt_auth.get_album(album_id)
        t0 = album["tracks"][0]

        # keys specific to playlist parsing
        assert "album" not in t0
        assert "thumbnails" not in t0
        assert "set_video_id" not in t0

        assert "name" in t0
        assert t0["artists"] == album["artists"]  # Tash is solo artist on this track

    def test_get_album_track_numbers(self, yt):
        # album with tracks completely removed/missing
        album = yt.get_album("MPREb_TPH4WqN5pUo")
        assert album["tracks"][0]["track_number"] == 3
        assert album["tracks"][13]["track_number"] == 18

        # album with track (#8) disabled/greyed out
        album = yt.get_album("MPREb_YuigcYm2erf")
        assert album["tracks"][7]["track_number"] is None

        # missing track numbers
        album = yt.get_album("MPREb_fMX7dnwhv65")
        assert "track_number" in (targ := album["tracks"][0])
        assert targ["track_number"] == 1

    def test_get_album_other_versions(self, yt):
        # Eminem - Curtain Call: The Hits (Explicit Variant)
        album = yt.get_album("MPREb_LQCAymzbaKJ")
        assert len(variants := album["other_versions"]) >= 1  # appears to be regional
        assert (variant := variants[0])["type"] == "Album"
        assert len(variant["artists"]) == 1
        assert variant["artists"][0] == {"name": "Eminem", "id": "UCedvOgsKFzcK3hA5taf3KoQ"}
        assert variant["playlist_id"] is not None

        # album that's multi-artist, a single, and has clean version
        # Cassö & RAYE - Prada
        album = yt.get_album("MPREb_of3qfisa0yU")
        assert not album["explicit"]
        assert (variant := album["other_versions"][0])["type"] == "Single"
        assert variant["explicit"]
        assert len(variant["artists"]) == 3
        assert variant["artists"][0]["id"] == "UCGWMNnI1Ky5bMcRlr73Cj2Q"
        assert variant["artists"][1]["name"] == "RAYE"
        assert variant["artists"][2] == {"id": "UCb7jnkQW94hzOoWkG14zs4w", "name": "D-Block Europe"}

    def test_get_album_parsing(self, yt):
        album = yt.get_album("MPREb_HLU4ajrAzcU")  # Flume - Palaces
        # album has a track with 3 artists, linked
        assert len(targ := album["tracks"][3]["artists"]) == 3
        # all artists should have ids
        assert len([x["id"] for x in targ if x["id"]]) == 3

        album = yt.get_album("MPREb_M4IdGHS6DyO")  # IMANU - Unfold
        # album has tracks with 3 unlinked artists
        assert len(targ := album["tracks"][3]["artists"]) == 3
        # test at least album artist is filled
        assert len([x["id"] for x in targ if x["id"]]) >= 1

    def test_get_song(self, config, yt, yt_oauth, sample_video):
        song = yt_oauth.get_song(config["uploads"]["private_upload_id"])  # private upload
        assert len(song) == 5
        song = yt.get_song(sample_video)
        assert len(song["streamingData"]["adaptiveFormats"]) >= 10

    def test_get_song_related_content(self, yt_oauth, sample_video):
        song = yt_oauth.get_watch_playlist(sample_video)
        song = yt_oauth.get_song_related(song["related"])
        assert len(song) >= 5

    def test_get_lyrics(self, config, yt, sample_video):
        playlist = yt.get_watch_playlist(sample_video)
        lyrics_song = yt.get_lyrics(playlist["lyrics"])
        assert lyrics_song["lyrics"] is not None
        assert lyrics_song["source"] is not None

        playlist = yt.get_watch_playlist(config["uploads"]["private_upload_id"])
        assert playlist["lyrics"] is None
        with pytest.raises(Exception):
            yt.get_lyrics(playlist["lyrics"])

    def test_get_signature_timestamp(self, yt):
        signature_timestamp = yt.get_signature_timestamp()
        assert signature_timestamp is not None

    def test_set_taste_profile(self, yt, yt_brand):
        with pytest.raises(Exception):
            yt.set_taste_profile(["not an artist"])
        taste_profile = yt.get_taste_profile()
        assert yt.set_taste_profile(list(taste_profile)[:5], taste_profile) is None

        with pytest.raises(Exception):
            yt_brand.set_taste_profile(["test", "test2"])
        taste_profile = yt_brand.get_taste_profile()
        assert yt_brand.set_taste_profile(list(taste_profile)[:1], taste_profile) is None

    def test_get_taste_profile(self, yt, yt_oauth):
        result = yt.get_taste_profile()
        assert len(result) >= 0

        result = yt_oauth.get_taste_profile()
        assert len(result) >= 0

    def test_get_search_suggestions(self, yt, yt_brand, yt_auth):
        result = yt.get_search_suggestions("fade")
        assert len(result) >= 0

        result = yt.get_search_suggestions("fade", detailed_runs=True)
        assert len(result) >= 0

        # add search term to history
        first_pass = yt_brand.search("b")
        assert len(first_pass) > 0

        # get results
        results = yt_auth.get_search_suggestions("b", detailed_runs=True)
        assert len(results) > 0
        assert any(not item["fromHistory"] for item in results)
