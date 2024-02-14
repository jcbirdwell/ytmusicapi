from typing import Annotated

from pydantic import Field, field_validator

from .base import FlexSchema


class CoreTrack(FlexSchema):
    video_id: str = Field(alias="videoId")
    name: str = Field(alias="title")
    duration_s: int = Field(alias="lengthSeconds")
    channel_id: str = Field(alias="channelId")
    crawlable: bool = Field(alias="isCrawlable")
    thumbnails: Annotated[list, Field(alias="thumbnail")] = []
    view_count: int = Field(alias="viewCount")
    author: str
    video_type: str = Field(alias="musicVideoType")

    @field_validator("thumbnails", mode="before")
    @classmethod
    def validate_thumbnails(cls, v: dict):
        return v.get("thumbnails", [])
