from .songs import parse_pl_song_artists, parse_song_album
from .utils import *


def parse_uploaded_items(results):
    songs = []
    for result in results:
        data = result[MRLIR]
        if "menu" not in data:
            continue

        song = {
            "entity_id": nav(data, MENU_ITEMS)[-1]["menuNavigationItemRenderer"]["navigationEndpoint"][
                "confirmDialogEndpoint"
            ]["content"]["confirmDialogRenderer"]["confirmButton"]["buttonRenderer"]["command"][
                "musicDeletePrivatelyOwnedEntityCommand"
            ]["entityId"],
            "video_id": nav(data, MENU_ITEMS + [0] + MENU_SERVICE)["queueAddEndpoint"]["queueTarget"][
                "videoId"
            ],
            "title": get_item_text(data, 0),
            "duration_s": parse_duration(get_fixed_column_item(data, 0)["text"]["runs"][0]["text"]),
            "artists": parse_pl_song_artists(data, 1),
            "album": parse_song_album(data, 2),
            "like_status": nav(data, MENU_LIKE_STATUS),
            "thumbnails": nav(data, THUMBNAILS) if "thumbnail" in data else None,
        }

        songs.append(song)

    return songs
