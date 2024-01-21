from ytmusicapi.helpers import to_int

from .songs import parse_like_status, parse_song_runs
from .utils import *


def parse_album_header(response):
    header = nav(response, HEADER_DETAIL)
    album = {
        "name": nav(header, TITLE_TEXT),
        "type": nav(header, SUBTITLE),
        "thumbnails": nav(header, THUMBNAIL_CROPPED),
        "explicit": nav(header, SUBTITLE_BADGE_LABEL, True) is not None,
    } | parse_song_runs(header["subtitle"]["runs"][2:])  # add keys from song runs to dict

    if "description" in header:
        album["description"] = header["description"]["runs"][0]["text"]

    if len(header["secondSubtitle"]["runs"]) > 1:
        album["track_count"] = to_int(header["secondSubtitle"]["runs"][0]["text"])
        album["duration_s"] = parse_duration(header["secondSubtitle"]["runs"][2]["text"])
    else:
        album["duration_s"] = parse_duration(header["secondSubtitle"]["runs"][0]["text"])
        album["track_count"] = None

    # add to library/uploaded
    top = nav(header, MENU)["topLevelButtons"]
    album["playlist_id"] = nav(top, [0, "buttonRenderer"] + NAVIGATION_WATCH_PLAYLIST_ID, True)
    if not album["playlist_id"]:
        album["playlist_id"] = nav(top, [0, "buttonRenderer"] + NAVIGATION_PLAYLIST_ID, True)
    album["like_status"] = parse_like_status(nav(top, [1, "buttonRenderer", "defaultServiceEndpoint"], True))

    return album
