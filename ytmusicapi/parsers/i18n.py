from typing import Dict, List

from ytmusicapi.parsers.browsing import (
    parse_album,
    parse_content_list,
    parse_playlist,
    parse_related_artist,
    parse_video,
)
from ytmusicapi.parsers.utils import get_ext, i18n


class Parser:
    def __init__(self, language):
        self.lang = language

    @i18n
    def get_search_result_types(self):
        return [
            _("artist"),
            _("playlist"),
            _("song"),
            _("video"),
            _("station"),
            _("profile"),
            _("podcast"),
            _("episode"),
        ]

    @i18n
    def append_channel_contents(self, channel: Dict, results: List) -> Dict:
        cat_map = {
            _("albums"): ("albums", parse_album),  # type: ignore[name-defined]
            _("singles"): ("singles", parse_album),  # type: ignore[name-defined]
            _("videos"): ("videos", parse_video),  # type: ignore[name-defined]
            _("playlists"): ("playlists", parse_playlist),  # type: ignore[name-defined]
            _("related"): ("related", parse_related_artist),  # type: ignore[name-defined]
            "featured on": ("features", parse_playlist),
        }

        for shelf in results:
            if not (render := shelf.get("musicCarouselShelfRenderer")):
                continue

            ext = get_ext(render["header"]["musicCarouselShelfBasicHeaderRenderer"])
            key, func = cat_map[ext.pop("text")]
            channel[key] = {"ext": ext, "items": parse_content_list(render["contents"], func)}

            if "artist_id" not in channel and ext["type"] == "MUSIC_PAGE_TYPE_ARTIST_DISCOGRAPHY":
                channel["artist_id"] = ext["browse_id"][4:]

        return channel
