from typing import Any, Dict, List

from .songs import *


def parse_watch_playlist(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tracks = []
    PPVWR = "playlistPanelVideoWrapperRenderer"
    PPVR = "playlistPanelVideoRenderer"
    for result in results:
        counterpart = None
        if PPVWR in result:
            counterpart = result[PPVWR]["counterpart"][0]["counterpartRenderer"][PPVR]
            result = result[PPVWR]["primaryRenderer"]
        if PPVR not in result:
            continue
        data = result[PPVR]
        if "unplayableText" in data:
            continue

        track = parse_watch_track(data)
        if counterpart:
            track["counterpart"] = parse_watch_track(counterpart)
        tracks.append(track)

    return tracks


def parse_watch_track(data):
    feedback_tokens = like_status = library_status = None
    for item in nav(data, MENU_ITEMS):
        if TOGGLE_MENU in item:
            library_status = parse_song_library_status(item)
            service = item[TOGGLE_MENU]["defaultServiceEndpoint"]
            if "feedbackEndpoint" in service:
                feedback_tokens = parse_song_menu_tokens(item)
            if "likeEndpoint" in service:
                like_status = parse_like_status(service)

    song_info = parse_song_runs(data["longBylineText"]["runs"])

    track = {
        "video_id": data["videoId"],
        "title": nav(data, TITLE_TEXT),
        "length": nav(data, ["lengthText", "runs", 0, "text"], True),
        "thumbnail": nav(data, THUMBNAIL),
        "feedback_tokens": feedback_tokens,
        "like_status": like_status,
        "in_library": library_status,
        "video_type": nav(data, ["navigationEndpoint"] + NAVIGATION_VIDEO_TYPE, True),
    }
    track.update(song_info)
    return track


def get_tab_browse_id(next_render, tab_id):
    if "unselectable" not in next_render["tabs"][tab_id]["tabRenderer"]:
        return next_render["tabs"][tab_id]["tabRenderer"]["endpoint"]["browseEndpoint"]["browseId"]
    else:
        return None
