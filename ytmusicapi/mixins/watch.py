from typing import Dict, List, Optional, Union

from ytmusicapi.continuations import get_continuations
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.watch import *


class WatchMixin(MixinProtocol):
    def get_watch_playlist(
        self,
        video_id: Optional[str] = None,
        playlist_id: Optional[str] = None,
        limit=25,
        radio: bool = False,
        shuffle: bool = False,
    ) -> Dict[str, Union[List[Dict], str, None]]:
        """
        Get a watch list of tracks. This watch playlist appears when you press
        play on a track in YouTube Music.

        Please note that the `INDIFFERENT` likeStatus of tracks returned by this
        endpoint may be either `INDIFFERENT` or `DISLIKE`, due to ambiguous data
        returned by YouTube Music.

        :param video_id: videoId of the played video
        :param playlist_id: playlistId of the played playlist or album
        :param limit: minimum number of watch playlist items to return
        :param radio: get a radio playlist (changes each time)
        :param shuffle: shuffle the input playlist. only works when the playlistId parameter
            is set at the same time. does not work if radio=True
        :return: List of watch playlist items. The counterpart key is optional and only
            appears if a song has a corresponding video counterpart (UI song/video
            switcher).

        Example::

            {
                "tracks": [
                    {
                      "videoId": "9mWr4c_ig54",
                      "title": "Foolish Of Me (feat. Jonathan Mendelsohn)",
                      "length": "3:07",
                      "thumbnail": [
                        {
                          "url": "https://lh3.googleusercontent.com/ulK2YaLtOW0PzcN7ufltG6e4ae3WZ9Bvg8CCwhe6LOccu1lCKxJy2r5AsYrsHeMBSLrGJCNpJqXgwczk=w60-h60-l90-rj",
                          "width": 60,
                          "height": 60
                        }...
                      ],
                      "feedbackTokens": {
                        "add": "AB9zfpIGg9XN4u2iJ...",
                        "remove": "AB9zfpJdzWLcdZtC..."
                      },
                      "likeStatus": "INDIFFERENT",
                      "videoType": "MUSIC_VIDEO_TYPE_ATV",
                      "artists": [
                        {
                          "name": "Seven Lions",
                          "id": "UCYd2yzYRx7b9FYnBSlbnknA"
                        },
                        {
                          "name": "Jason Ross",
                          "id": "UCVCD9Iwnqn2ipN9JIF6B-nA"
                        },
                        {
                          "name": "Crystal Skies",
                          "id": "UCTJZESxeZ0J_M7JXyFUVmvA"
                        }
                      ],
                      "album": {
                        "name": "Foolish Of Me",
                        "id": "MPREb_C8aRK1qmsDJ"
                      },
                      "year": "2020",
                      "counterpart": {
                        "videoId": "E0S4W34zFMA",
                        "title": "Foolish Of Me [ABGT404] (feat. Jonathan Mendelsohn)",
                        "length": "3:07",
                        "thumbnail": [...],
                        "feedbackTokens": null,
                        "likeStatus": "LIKE",
                        "artists": [
                          {
                            "name": "Jason Ross",
                            "id": null
                          },
                          {
                            "name": "Seven Lions",
                            "id": null
                          },
                          {
                            "name": "Crystal Skies",
                            "id": null
                          }
                        ],
                        "views": "6.6K"
                      }
                    },...
                ],
                "playlistId": "RDAMVM4y33h81phKU",
                "lyrics": "MPLYt_HNNclO0Ddoc-17"
            }

        """
        if not video_id and not playlist_id:
            raise Exception("You must provide either a video id, a playlist id, or both")

        body = {
            "enablePersistentPlaylistPanel": True,
            "isAudioOnly": True,
            "tunerSettingValue": "AUTOMIX_SETTING_NORMAL",
        }
        if video_id:
            body["videoId"] = video_id
            if not playlist_id:
                playlist_id = "RDAMVM" + video_id
            if not (radio or shuffle):
                body["watchEndpointMusicSupportedConfigs"] = {
                    "watchEndpointMusicConfig": {
                        "hasPersistentPlaylistPanel": True,
                        "musicVideoType": "MUSIC_VIDEO_TYPE_ATV",
                    }
                }
        is_playlist = False
        if playlist_id:
            playlist_id = playlist_id.lstrip("VL")
            is_playlist = playlist_id.startswith("PL") or playlist_id.startswith("OLA")
            body["playlistId"] = playlist_id

        if shuffle and playlist_id is not None:
            body["params"] = "wAEB8gECKAE%3D"
        if radio:
            body["params"] = "wAEB"
        endpoint = "next"
        response = self._send_request(endpoint, body)
        next_render = nav(
            response,
            [
                "contents",
                "singleColumnMusicWatchNextResultsRenderer",
                "tabbedRenderer",
                "watchNextTabbedResultsRenderer",
            ],
        )

        results = nav(next_render, TAB_CONTENT + ["musicQueueRenderer", "content", "playlistPanelRenderer"])

        output = {
            "lyrics": get_tab_browse_id(next_render, 1),
            "related": get_tab_browse_id(next_render, 2),
            "tracks": parse_watch_playlist(results["contents"]),
            "playlist": next(
                (
                    x
                    for x in results["contents"]
                    if nav(x, ["playlistPanelVideoRenderer"] + NAVIGATION_PLAYLIST_ID, True)
                ),
                None,
            ),
        }

        if "continuations" in results:
            request_func = lambda additional_params: self._send_request(endpoint, body, additional_params)
            parse_func = lambda contents: parse_watch_playlist(contents)
            output["tracks"].extend(
                get_continuations(
                    results,
                    "playlistPanelContinuation",
                    limit - len(output["tracks"]),
                    request_func,
                    parse_func,
                    "" if is_playlist else "Radio",
                )
            )

        return output
