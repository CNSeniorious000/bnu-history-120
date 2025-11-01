from typing import Literal

from typing_extensions import TypeAlias, TypedDict

from .data import name_count_map


class PartialPage(TypedDict):
    title: str
    div: str


Universities = Literal["北师大", "辅大", "女高师"]
Categories = Literal["校长", "校友", "教师", "创始人"]
Names: TypeAlias = Literal.__getitem__(tuple(name_count_map.keys()))  # type: ignore
