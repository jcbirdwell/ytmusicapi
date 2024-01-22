import re

from .utils import *


def parse_pl_song_artists(data, index, as_album=None):
    flex_item = get_flex_column_item(data, index)
    if not flex_item:
        return None

    artists = artists_from_runs(flex_item["text"]["runs"], 0)
    # check if track came from album without linked artists
    if len(artists) == 1 and artists[0]["id"] is None:
        # rsplit and pray that artist doesn't have an ampersand in their name
        seperated = artists[0]["name"].rsplit(" & ", 1)
        if len(seperated) == 1:
            parsed = seperated[0]
        else:
            parsed = [item.rstrip().lstrip() for item in seperated[0].split(",") if item] + [seperated[-1]]

        # try to fill with name and id from album artists when possible
        return [
            next((f for f in as_album["artists"] if f["name"] == x), {"name": x, "id": None})
            if as_album
            else {"name": x, "id": None}
            for x in parsed
        ]

    return artists


def parse_id_name(sub_run):
    """Return id and name from an artist or user subtitle runs"""
    return {
        "id": nav(sub_run, NAVIGATION_BROWSE_ID, True),
        "name": nav(sub_run, ["text"], True),
    }


def artists_from_runs(runs, offset=2):
    """Parse artists name and id from runs WITH separators"""
    if not runs:
        return []

    return [parse_id_name(runs[idx]) for idx in range(offset, len(runs), 2)]


def parse_song_runs(runs):
    parsed = {"artists": []}
    for i, run in enumerate(runs):
        if i % 2:  # uneven items are always separators
            continue

        if "navigationEndpoint" in run:  # artist or album
            item = parse_id_name(run)

            if item["id"] and (item["id"].startswith("MPRE") or "release_detail" in item["id"]):  # album
                parsed["album"] = item
            else:  # artist
                parsed["artists"].append(item)

        else:
            # note: YT uses non-breaking space \xa0 to separate number and magnitude
            if re.match(r"^\d([^ ])* [^ ]*$", run["text"]) and i > 0:
                parsed["views"] = run["text"].split(" ")[0]

            elif re.match(r"^(\d+:)*\d+:\d+$", run["text"]):
                parsed["duration_s"] = parse_duration(run["text"])

            elif re.match(r"^\d{4}$", run["text"]):
                parsed["year"] = run["text"]

            else:  # artist without id
                parsed["artists"].append({"name": run["text"], "id": None})

    return parsed


def parse_song_album(data, index):
    flex_item = get_flex_column_item(data, index)
    if not flex_item:
        return {"id": None, "name": None}
    else:
        return {"name": get_item_text(data, index), "id": get_browse_id(flex_item, 0)}


def parse_song_library_status(item) -> bool:
    """Returns True if song is in the library"""
    return nav(item, [TOGGLE_MENU, "defaultIcon", "iconType"], True) == "LIBRARY_SAVED"


def parse_song_menu_tokens(item):
    toggle_menu = item[TOGGLE_MENU]

    library_add_token = nav(toggle_menu, ["defaultServiceEndpoint"] + FEEDBACK_TOKEN, True)
    library_remove_token = nav(toggle_menu, ["toggledServiceEndpoint"] + FEEDBACK_TOKEN, True)

    in_library = parse_song_library_status(item)
    if in_library:
        library_add_token, library_remove_token = library_remove_token, library_add_token

    return {"add": library_add_token, "remove": library_remove_token}


# todo: ensure this works with disliked
def parse_like_status(service):
    if service is None:
        return None
    return next((x for x in ["LIKE", "INDIFFERENT"] if x != service["likeEndpoint"]["status"]), None)
