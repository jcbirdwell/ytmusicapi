import time

import pytest


class TestPlaylists:
    def test_get_playlist_foreign(self, yt, yt_auth, yt_oauth):
        with pytest.raises(Exception):
            yt.get_playlist("PLABC")
        playlist = yt_auth.get_playlist("PLk5BdzXBUiUe8Q5I13ZSCD8HbxMqJUUQA", limit=300, suggestions_limit=7)
        assert len(playlist["duration"]) > 5
        assert len(playlist["tracks"]) > 200
        assert "suggestions" not in playlist

        yt.get_playlist("RDATgXd-")
        assert len(playlist["tracks"]) >= 100

        playlist = yt_oauth.get_playlist("PLj4BSJLnVpNyIjbCWXWNAmybc97FXLlTk", limit=None, related=True)
        assert len(playlist["tracks"]) > 200
        assert len(playlist["related"]) == 0

    def test_get_playlist_owned(self, config, yt_brand):
        playlist = yt_brand.get_playlist(config["playlists"]["own"], related=True, suggestions_limit=21)
        assert len(playlist["tracks"]) < 100
        assert len(playlist["suggestions"]) == 21
        assert len(playlist["related"]) == 10

    def test_edit_playlist(self, config, yt_brand):
        playlist = yt_brand.get_playlist(config["playlists"]["own"])
        response = yt_brand.edit_playlist(
            playlist["id"],
            title="",
            description="",
            privacy_status="PRIVATE",
            move_item=(
                playlist["tracks"][1]["set_video_id"],
                playlist["tracks"][0]["set_video_id"],
            ),
        )
        assert response == "STATUS_SUCCEEDED", "Playlist edit failed"
        yt_brand.edit_playlist(
            playlist["id"],
            title=playlist["name"],
            description=playlist["description"],
            privacy_status=playlist["privacy"],
            move_item=(
                playlist["tracks"][0]["set_video_id"],
                playlist["tracks"][1]["set_video_id"],
            ),
        )
        assert response == "STATUS_SUCCEEDED", "Playlist edit failed"

    def test_end2end(self, config, yt_brand, sample_video):
        playlist_id = yt_brand.create_playlist(
            "test",
            "test description",
            source_playlist="OLAK5uy_lGQfnMNGvYCRdDq9ZLzJV2BJL2aHQsz9Y",
        )
        assert len(playlist_id) == 34, "Playlist creation failed"
        yt_brand.edit_playlist(playlist_id, add_to_top=True)
        response = yt_brand.add_playlist_items(
            playlist_id,
            [sample_video, sample_video],
            source_playlist="OLAK5uy_nvjTE32aFYdFN7HCyMv3cGqD3wqBb4Jow",
            duplicates=True,
        )
        assert response["status"] == "STATUS_SUCCEEDED", "Adding playlist item failed"
        assert len(response["playlistEditResults"]) > 0, "Adding playlist item failed"
        time.sleep(3)
        yt_brand.edit_playlist(playlist_id, add_to_top=False)
        playlist = yt_brand.get_playlist(playlist_id, related=True)
        assert len(playlist["tracks"]) == 46, "Getting playlist items failed"
        response = yt_brand.remove_playlist_items(playlist_id, playlist["tracks"])
        assert response == "STATUS_SUCCEEDED", "Playlist item removal failed"
        yt_brand.delete_playlist(playlist_id)

    def test_playlist_edge_cases(self, yt):
        test_pl = yt.get_playlist("VLPLlkifUmkICT6noeEfgsphp-t3gT9XcpTc")  # test track playlist
        assert len(test_pl["tracks"]) == test_pl["track_count"]
        outer = next((track for track in test_pl["tracks"] if track["video_id"] == "P57tM6HVW-Q"), None)
        assert outer is not None
        assert len(outer["artists"]) == 1
        assert outer["artists"][0]["name"] == "Joey Gx"
        assert outer["artists"][0]["id"] is None
