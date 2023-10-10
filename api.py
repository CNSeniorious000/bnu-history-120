from collections import defaultdict
from contextlib import suppress
from functools import lru_cache
from sys import version_info
from traceback import format_exc
from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, Header
from fastapi.responses import ORJSONResponse, PlainTextResponse, StreamingResponse
from pydantic import AnyHttpUrl, BaseModel, Field
from typing_extensions import NotRequired, TypedDict

from core import template
from models import Categories, Names, PartialPage, Universities
from person import name_count_map, people, render_person_html, render_university_html, universities

router = APIRouter(prefix="/api")


@router.get("/people/list", response_model=List[str])
@lru_cache(None)
def get_name_set():
    return ORJSONResponse(list(name_count_map))


@router.get("/people/dict", response_model=Dict[str, List[AnyHttpUrl]])
@lru_cache(None)
def get_people_map():
    name_map = defaultdict(list)
    for person in people:
        name_map[person.name].append(person.url)

    return ORJSONResponse(name_map)


@router.get("/{university}", response_model=PartialPage)
def get_university_md(university: Universities):
    with suppress(NotADirectoryError):
        html = render_university_html(university)
        university_full_name = universities[university].full_name
        return ORJSONResponse(
            {
                "div": template.get_template("Article.jinja2").render(
                    {"name": university_full_name, "markdown": html}
                ),
                "title": university_full_name,
            }
        )

    return PlainTextResponse(format_exc(chain=False), 404)


@router.get("/{university}/{category}/{name}", response_model=PartialPage)
def get_person_md(university: Universities, category: Categories, name: Names):
    with suppress(NotADirectoryError, FileNotFoundError):
        html = render_person_html(name, university, category)
        return ORJSONResponse(
            {
                "div": template.get_template("Article.jinja2").render(
                    {"name": name, "markdown": html}
                ),
                "title": f"{name} - {university}{category}",
            }
        )

    return PlainTextResponse(format_exc(chain=False), 404)


if version_info >= (3, 10):
    from os import getenv

    from dotenv import load_dotenv
    from promplate.llm.openai import AsyncChatGenerate, openai

    load_dotenv()

    agenerate = AsyncChatGenerate(model=getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"))

    if env_api_key := getenv("OPENAI_API_KEY"):
        openai.api_key = env_api_key

    if env_api_base := getenv("OPENAI_API_BASE"):
        openai.api_base = env_api_base
else:
    agenerate = lambda *_, **__: iter("This is a stub. Real functionality requires Python 3.10+")


class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str
    name: NotRequired[str]


class CreateChatCompletion(BaseModel):
    messages: List[Message] = Field(exclude=True)
    temperature: Optional[float] = Field(None, examples=[None], ge=0, le=1)
    top_p: Optional[float] = Field(None, examples=[None], ge=0, le=1)
    frequency_penalty: Optional[float] = Field(None, examples=[None], ge=-2, le=2)
    presence_penalty: Optional[float] = Field(None, examples=[None], ge=-2, le=2)


@router.post("/chat")
async def chat_complete(
    data: CreateChatCompletion, api_key: str = Header("", alias="Authorization")
) -> str:
    return StreamingResponse(
        agenerate(data.messages, **data.model_dump(exclude_defaults=True), api_key=api_key),
        media_type="text/plain",
    )
