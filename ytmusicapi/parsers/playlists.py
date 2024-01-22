from typing import List, Optional

from .songs import *


def parse_playlist_items(results, menu_entries: Optional[List[List]] = None, as_album=None):
    songs = []
    for result in results:
        if not (data := result.get(MRLIR, {})):
            continue
        if (title := get_item_text(data, 0) if "menu" in data else None) == "Song deleted":
            continue

        song = {
            "video_id": None,
            "title": title,
            "artists": parse_pl_song_artists(data, 1, as_album=as_album),
            "album": parse_song_album(data, 2),
            "like_status": None,
            "in_library": None,
            "thumbnails": None,
            "available": data.get("musicItemRendererDisplayPolicy", "GOOD_TO_GO") != UNAVAILABLE,
            "explicit": nav(data, BADGE_LABEL, True) is not None,
            "video_type": None,
            "set_video_id": None,
            "feedback_tokens": None,
        }

        # if the item has a menu, find its setVideoId
        if "menu" in data:
            # fixme: this
            for item in nav(data, MENU_ITEMS):
                if "menuServiceItemRenderer" in item:
                    menu_service = nav(item, MENU_SERVICE)
                    if "playlistEditEndpoint" in menu_service:
                        song["set_video_id"] = nav(
                            menu_service, ["playlistEditEndpoint", "actions", 0, "setVideoId"], True
                        )
                        song["video_id"] = nav(
                            menu_service, ["playlistEditEndpoint", "actions", 0, "removedVideoId"], True
                        )

                if TOGGLE_MENU in item:
                    song["feedback_tokens"] = parse_song_menu_tokens(item)
                    song["in_library"] = parse_song_library_status(item)

        # if item is not playable, the videoId was retrieved above
        # fixme: if the above is true, integrate into above id pull
        if (
            play := nav(data, PLAY_BUTTON, none_if_absent=True)
        ) is not None and "playNavigationEndpoint" in play:
            song["video_id"] = play["playNavigationEndpoint"]["watchEndpoint"]["videoId"]

            if "menu" in data:
                song["like_status"] = nav(data, MENU_LIKE_STATUS, True)

        if song["album"]["name"] is None and song["album"]["id"] is None:
            # views currently only present on albums and formatting is localization-dependent -> no parsing
            if get_item_text(data, 2) is not None and as_album:
                song["album"] = {"id": as_album["browse_id"], "name": as_album["name"]}

        if "fixedColumns" in data:
            # two variations
            if "simpleText" in (fork := get_fixed_column_item(data, 0)["text"]):
                song["duration_s"] = parse_duration(fork["simpleText"])
            else:
                song["duration_s"] = parse_duration(fork["runs"][0]["text"])

        if "thumbnail" in data:
            song["thumbnails"] = nav(data, THUMBNAILS)

        song["video_type"] = nav(
            data,
            MENU_ITEMS + [0, "menuNavigationItemRenderer", "navigationEndpoint"] + NAVIGATION_VIDEO_TYPE,
            True,
        )

        if as_album is not None:
            song["track_number"] = int(nav(data, ["index", "runs", 0, "text"])) if song["available"] else None

        if menu_entries:
            for menu_entry in menu_entries:
                if menu_entry[-1] == "feedbackToken":
                    song["feedback_token"] = nav(data, MENU_ITEMS + menu_entry)
                else:
                    song[menu_entry[-1]] = nav(data, MENU_ITEMS + menu_entry)

        songs.append(song)

    return songs
