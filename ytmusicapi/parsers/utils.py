import re
from functools import wraps

from ytmusicapi.navigation import *


def parse_menu_playlists(data, result):
    watch_menu = find_objects_by_key(nav(data, MENU_ITEMS), "menuNavigationItemRenderer")
    for item in [_x["menuNavigationItemRenderer"] for _x in watch_menu]:
        icon = nav(item, ["icon", "iconType"])
        if icon == "MUSIC_SHUFFLE":
            watch_key = "shuffleId"
        elif icon == "MIX":
            watch_key = "radioId"
        else:
            continue

        watch_id = nav(item, ["navigationEndpoint", "watchPlaylistEndpoint", "playlistId"], True)
        if not watch_id:
            watch_id = nav(item, ["navigationEndpoint", "watchEndpoint", "playlistId"], True)
        if watch_id:
            result[watch_key] = watch_id


def get_item_text(item, index, run_index=0, none_if_absent=False):
    column = get_flex_column_item(item, index)
    if not column:
        return None
    if none_if_absent and len(column["text"]["runs"]) < run_index + 1:
        return None
    return column["text"]["runs"][run_index]["text"]


def get_flex_column_item(item, index):
    if (
        len(item["flexColumns"]) <= index
        or "text" not in item["flexColumns"][index]["musicResponsiveListItemFlexColumnRenderer"]
        or "runs" not in item["flexColumns"][index]["musicResponsiveListItemFlexColumnRenderer"]["text"]
    ):
        return None

    return item["flexColumns"][index]["musicResponsiveListItemFlexColumnRenderer"]


def get_fixed_column_item(item, index):
    if (
        "text" not in item["fixedColumns"][index]["musicResponsiveListItemFixedColumnRenderer"]
        or "runs" not in item["fixedColumns"][index]["musicResponsiveListItemFixedColumnRenderer"]["text"]
    ):
        return None

    return item["fixedColumns"][index]["musicResponsiveListItemFixedColumnRenderer"]


def get_browse_id(item, index):
    if "navigationEndpoint" not in item["text"]["runs"][index]:
        return None
    else:
        return nav(item["text"]["runs"][index], NAVIGATION_BROWSE_ID)


def get_ext(item):
    base = item["title"]["runs"][0]

    if more := base.get("navigationEndpoint"):
        return {
            "text": base["text"].lower(),
            "browse_id": more["browseEndpoint"]["browseId"],
            "params": more["browseEndpoint"]["params"],
            "type": get_page_type(more["browseEndpoint"]),
        }
    else:
        return {"text": base["text"].lower(), "browse_id": None, "params": None, "type": None}


def get_page_type(item):
    if "browseEndpointContextSupportedConfigs" not in item:
        return None

    return item["browseEndpointContextSupportedConfigs"]["browseEndpointContextMusicConfig"]["pageType"]


def get_dot_separator_index(runs):
    index = len(runs)
    try:
        index = runs.index({"text": " • "})
    except ValueError:
        len(runs)
    return index


def parse_real_count(run):
    """Pull an int from views, plays, or subs"""
    if not run or "text" not in run:
        return -1
    count = run["text"].split(" ")[0]
    for fx in [("K", 1_000), ("M", 1_000_000), ("B", 1_000_000_000)]:
        if fx[0] in count:
            return int(float(count.replace(fx[0], "")) * fx[1])

    return int(count.replace(",", ""))


def parse_duration(duration):
    if duration is None:
        return duration
    if ":" in duration:
        mapped_increments = zip([1, 60, 3600], reversed(duration.split(":")))
        seconds = sum(multiplier * int(time) for multiplier, time in mapped_increments)
        return seconds
    elif "seconds" in duration or "minutes" in duration:
        matches = re.findall(r"(?:(\d*) hour)?(?:, )?(?:(\d*) minutes)?(?:, )?(?:(\d*) seconds)?", duration)
        hours, minutes, seconds = [int(x) if x else 0 for x in matches[0]]
        return seconds + minutes * 60 + hours * 3600


def i18n(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        method.__globals__["_"] = self.lang.gettext
        return method(self, *method_args, **method_kwargs)

    return _impl
